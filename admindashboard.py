# admin/dashboard.py
import streamlit as st
import pandas as pd
from database import (
    add_user, delete_user, get_all_users, add_section, get_all_sections,
    assign_section_to_teacher, assign_section_to_student,
    get_db_connection, get_users_with_sections, get_user  # Added get_user here
)


def get_users_with_sections():
    """Retrieve all users with their assigned sections"""
    conn = get_db_connection()
    students = conn.execute("""
        SELECT u.id, u.username, s.section_name
        FROM users u
        LEFT JOIN student_sections ss ON u.id = ss.student_id
        LEFT JOIN sections s ON ss.section_id = s.id
        WHERE u.role = 'Student'
    """).fetchall()

    teachers = conn.execute("""
        SELECT u.id, u.username, s.section_name
        FROM users u
        LEFT JOIN teacher_sections ts ON u.id = ts.teacher_id
        LEFT JOIN sections s ON ts.section_id = s.id
        WHERE u.role = 'Teacher'
    """).fetchall()
    conn.close()
    return students, teachers

def manage_users():
    """User management interface"""
    st.subheader("User Management")
    
    with st.expander("Create New Account", expanded=True):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["Student", "Teacher", "Admin"])
        
        sections = get_all_sections()
        section_options = {s["section_name"]: s["id"] for s in sections}

        if new_role == "Student":
            selected_section = st.selectbox("Assign Section", section_options.keys())
        elif new_role == "Teacher":
            selected_sections = st.multiselect("Assign Sections", section_options.keys())

        if st.button("Create User"):
            if new_username and new_password:
                if add_user(new_username, new_password, new_role):
                    user = get_user(new_username)
                    if user:
                        user_id = user["id"]
                        if new_role == "Student":
                            assign_section_to_student(user_id, section_options[selected_section])
                        elif new_role == "Teacher":
                            for section in selected_sections:
                                assign_section_to_teacher(user_id, section_options[section])
                        st.rerun()
                else:
                    st.error("Username already exists!")

def manage_sections():
    """Section management interface"""
    st.subheader("Section Management")
    
    with st.expander("Create New Section", expanded=True):
        new_section = st.text_input("Section Name")
        if st.button("Create Section"):
            if new_section:
                if add_section(new_section):
                    st.success("Section created!")
                    st.rerun()
                else:
                    st.error("Section name exists!")
    
    with st.expander("All Sections", expanded=True):
        sections = get_all_sections()
        if sections:
            df = pd.DataFrame([dict(s) for s in sections])
            st.dataframe(df[["id", "section_name"]], use_container_width=True)
        else:
            st.info("No sections found")

def admin_dashboard():
    """Main admin dashboard interface"""
    st.header("🔑 Admin Dashboard")
    
    # Metrics
    conn = get_db_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_sections = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
    conn.close()

    col1, col2 = st.columns(2)
    col1.metric("Total Users", total_users)
    col2.metric("Active Sections", total_sections)
    
    # Management tabs
    tab1, tab2 = st.tabs(["👥 User Management", "📂 Section Management"])
    
    with tab1:
        manage_users()
    
    with tab2:
        manage_sections()
    
    # Display assignments
    st.divider()
    st.subheader("Current Assignments")
    students, teachers = get_users_with_sections()
    
    if students or teachers:
        col1, col2 = st.columns(2)
        with col1:
            if students:
                st.dataframe(
                    pd.DataFrame([dict(s) for s in students]),
                    column_config={"id": "ID", "username": "Username", "section_name": "Section"},
                    use_container_width=True
                )
        with col2:
            if teachers:
                st.dataframe(
                    pd.DataFrame([dict(t) for t in teachers]),
                    column_config={"id": "ID", "username": "Username", "section_name": "Section"},
                    use_container_width=True
                )
    else:
        st.info("No section assignments found")

def manage_users():
    """User management interface"""
    st.subheader("User Management")
    
    with st.expander("Create New Account", expanded=True):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["Student", "Teacher", "Admin"])
        
        sections = get_all_sections()
        section_options = {s["section_name"]: s["id"] for s in sections}

        if new_role == "Student":
            selected_section = st.selectbox("Assign Section", section_options.keys())
        elif new_role == "Teacher":
            selected_sections = st.multiselect("Assign Sections", section_options.keys())

        if st.button("Create User"):
            if new_username and new_password:
                if add_user(new_username, new_password, new_role):
                    user = get_user(new_username)
                    if user:
                        user_id = user["id"]
                        if new_role == "Student":
                            assign_section_to_student(user_id, section_options[selected_section])
                        elif new_role == "Teacher":
                            for section in selected_sections:
                                assign_section_to_teacher(user_id, section_options[section])
                        st.rerun()
                else:
                    st.error("Username already exists!")

    st.subheader("Existing Users")

    users = get_all_users()  # Get all users from the database
    
    if users:
        user_df = pd.DataFrame(users)
        user_df = user_df[["id", "username", "role"]]  # Display only relevant columns
        
        for _, row in user_df.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(f"**{row['username']}**")
            col2.write(f"🛠️ Role: {row['role']}")
            with col3:
                if st.button("❌ Delete", key=f"del_{row['id']}"):
                    if delete_user(row['id']):
                        st.success(f"Deleted {row['username']} successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete {row['username']}")
    else:
        st.info("No users found.")


