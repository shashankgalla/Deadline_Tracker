import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
import streamlit_authenticator as stauth

import streamlit as st
import streamlit_authenticator as stauth

# Define the credentials (username and password) for allowed users
names = ['User One', 'User Two']
usernames = ['user1', 'user2']
passwords = ['password1', 'password2']

# Hash the passwords for security
hashed_passwords = stauth.Hasher(passwords).generate()

# Set up the authenticator with proper parameters
credentials = {
    "usernames": {
        "user1": {"name": "User One", "password": hashed_passwords[0]},
        "user2": {"name": "User Two", "password": hashed_passwords[1]},
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="streamlit_auth",      # Custom cookie name
    cookie_key="auth_key",             # Secret key for cookie signature
    cookie_expiry_days=1               # Cookie expiry
)

# Create a login form
name, authentication_status, username = authenticator.login("Login", "main")  # "main" must be lowercase

# Handle the authentication status
if authentication_status:
    st.success(f"Welcome {name}!")
    st.write("Only authenticated users can access this area.")
    # Add your app logic here
elif authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password")




# Connect to the SQLite database
conn = sqlite3.connect('deadlines_db.sqlite')
cursor = conn.cursor()

# Function to add new tasks (with date and time)
def add_task(task_name, start_date, deadline_date):
    cursor.execute('''
        INSERT INTO tasks (task_name, start_date, deadline_date)
        VALUES (?, ?, ?)
    ''', (task_name, start_date.strftime('%Y-%m-%d %H:%M:%S'), deadline_date.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()

# Function to get tasks for a specific date
def get_tasks_by_date(selected_date):
    query = "SELECT id, task_name, deadline_date FROM tasks WHERE date(deadline_date) = ?"
    cursor.execute(query, (selected_date,))
    return cursor.fetchall()

# Function to delete a task by ID
def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()

# Streamlit App
st.title("📧 Real-Time Deadline Tracker")
st.markdown("""
    Welcome to your personalized deadline tracker! Here, you can add tasks, view tasks by date, and manage deadlines in a streamlined way.
""")

# Sidebar for daily updates
with st.sidebar:
    st.header("📝 Add New Task")
    task_name = st.text_input("Task Name")
    
    # Start Date
    start_date = st.date_input("Start Date", datetime.today())
    
    # Custom time input for Start Time
    start_hour = st.number_input("Start Hour (0-23)", min_value=0, max_value=23, value=datetime.now().hour)
    start_minute = st.number_input("Start Minute (0-59)", min_value=0, max_value=59, value=datetime.now().minute)
    start_time = time(start_hour, start_minute)

    # Deadline Date
    deadline_date = st.date_input("Deadline Date", datetime.today())

    # Custom time input for Deadline Time
    deadline_hour = st.number_input("Deadline Hour (0-23)", min_value=0, max_value=23, value=datetime.now().hour)
    deadline_minute = st.number_input("Deadline Minute (0-59)", min_value=0, max_value=59, value=datetime.now().minute)
    deadline_time = time(deadline_hour, deadline_minute)

    # Combine the date and time fields
    start_datetime = datetime.combine(start_date, start_time)
    deadline_datetime = datetime.combine(deadline_date, deadline_time)

    if st.button("Add Task"):
        add_task(task_name, start_datetime, deadline_datetime)
        st.success("Task added successfully!")

# Display today's deadlines
st.header(f"📅 Deadlines for Today ({datetime.now().date()}):")
tasks_due_today = get_tasks_by_date(datetime.now().strftime('%Y-%m-%d'))

# Apply custom CSS to style the table and background
st.markdown("""
    <style>
    body {
        background-color: #f0f8ff;
        font-family: 'Arial', sans-serif;
    }
    .styled-table {
        font-size: 18px;
        border-collapse: collapse;
        margin: 25px 0;
        width: 100%;
        color: #333;
    }
    .styled-table th, .styled-table td {
        border: 1px solid #dddddd;
        text-align: center;
        padding: 12px;
        max-width: 200px;  /* Set a max width to handle large text */
        word-wrap: break-word; /* Force long text to wrap */
    }
    .styled-table th {
        background-color: #ffcccb; /* Light pink */
        font-weight: bold;
        color: #333;
    }
    .styled-table tr:nth-child(even) {
        background-color: #f0f0f0; /* Light gray for even rows */
    }
    .styled-table tr:nth-child(odd) {
        background-color: #ffffff; /* White for odd rows */
    }
    .table-container {
        overflow-x: auto; /* Allow horizontal scrolling if needed */
    }
    </style>
    """, unsafe_allow_html=True)

# Display the table with custom styling
if tasks_due_today:
    df_today = pd.DataFrame(tasks_due_today, columns=["ID", "Task Name", "Deadline"])
    df_today['Deadline'] = pd.to_datetime(df_today['Deadline'])
    
    # Sort by Deadline time
    df_today = df_today.sort_values(by='Deadline', ascending=True)

    # Format deadline to display as '%Y-%m-%d %H:%M:%S'
    df_today['Deadline'] = df_today['Deadline'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Convert the DataFrame to an HTML table with custom CSS styling
    st.markdown(f"""
    <div class="table-container">
    <table class="styled-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Task Name</th>
                <th>Deadline</th>
            </tr>
        </thead>
        <tbody>
            {"".join([f"<tr><td>{row.ID}</td><td>{row['Task Name']}</td><td>{row.Deadline}</td></tr>" for index, row in df_today.iterrows()])}
        </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No tasks due today.")

# Section to view deadlines by selected date
st.header("🔍 View Deadlines by Custom Date")
selected_date = st.date_input("Select a Date")
tasks_selected_date = get_tasks_by_date(selected_date.strftime('%Y-%m-%d'))

if tasks_selected_date:
    st.subheader(f"Deadlines for {selected_date}:")
    df_selected = pd.DataFrame(tasks_selected_date, columns=["ID", "Task Name", "Deadline"])
    df_selected['Deadline'] = pd.to_datetime(df_selected['Deadline'])
    df_selected['Deadline'] = df_selected['Deadline'].dt.strftime('%Y-%m-%d %H:%M:%S')
    st.dataframe(df_selected)
else:
    st.info(f"No tasks due for {selected_date}.")

# Section to delete tasks
st.header("🗑️ Delete a Task")
if tasks_selected_date:
    task_id_to_delete = st.selectbox("Select Task ID to Delete", df_selected['ID'].values)
    if st.button("Delete Task"):
        delete_task(task_id_to_delete)
        st.warning("Task deleted! Please refresh to see updated tasks.")

# Footer aesthetics
st.markdown("---")
st.write("Made with ❤️ by Shashank, using Streamlit to keep track of your deadlines.")
st.markdown("Stay organized and never miss a deadline again!")

# Close the database connection
conn.close()

