import streamlit as st
from passlib.hash import pbkdf2_sha256
from ultralytics import YOLO
import cv2
import math
import cvzone
import tempfile
import numpy as np
import base64


import sqlite3
import smtplib
s = smtplib.SMTP('smtp.gmail.com', 587)
from playsound import playsound
s.starttls()
s.login("reddybhagyesh12@gmail.com", "qlidysemvuxbfxoa")
message = "Violence is detected"
# def home_page():
#     st.title("Human Surveillance System")
#     st.write("Welcome to the Human Surveillance System, a cutting-edge platform leveraging the power of YOLOv8 for real-time pothole detection.")
#     st.write("Our advanced solution employs state-of-the-art computer vision and deep learning technologies to accurately identify potholes in images, video streams, and live webcam feeds.")
#     st.write("To fully explore and utilize the features of the system, please proceed to log in or sign up to gain access.")
def home_page():
    st.markdown("""
    <style>
    .title {
        font-family: 'Arial', sans-serif;
        font-size: 50px;
        color: #4B9CD3;
        font-weight: bold;
        text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);
        transform: rotate(0.1deg);
        letter-spacing: 2px;
    }
    .description {
        font-family: 'Arial', sans-serif;
        font-size: 20px;
        color: #333;
        font-weight: 500;
    }
    </style>
    <h1 class="title">Human Surveillance System</h1>
    <p class="description">Welcome to the Human Surveillance System, a cutting-edge platform leveraging the power of YOLOv8 for real-time pothole detection.</p>
    <p class="description">Our advanced solution employs state-of-the-art computer vision and deep learning technologies to accurately identify potholes in images, video streams, and live webcam feeds.</p>
    <p class="description">To fully explore and utilize the features of the system, please proceed to log in or sign up to gain access.</p>
    """, unsafe_allow_html=True)

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn
def create_table(conn):
    """ Create a table for storing user data """
    try:
        sql = '''CREATE TABLE IF NOT EXISTS users (
                    username text PRIMARY KEY,
                    password text NOT NULL
                 );'''
        conn.execute(sql)
    except Exception as e:
        print(e)



# Function to set the background image
def set_background_image(image_file):
    with open(image_file, "rb") as file:
        base64_image = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{base64_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image
set_background_image('bg4.png')

# Initialize session state for user authentication
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# User database simulation (in-memory)
users = {}

# Initialize session state for user data if not already present
if 'users' not in st.session_state:
    st.session_state['users'] = {}

def signup(username, password, conn):
    """ Sign up a new user """
    try:
        hashed_password = pbkdf2_sha256.hash(password)
        sql = ''' INSERT INTO users(username,password)
                  VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (username, hashed_password))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def login(username, password):
    st.text(f"Debug: Users currently in system: {st.session_state['users']}")  # For debugging
    if username in st.session_state['users'] and pbkdf2_sha256.verify(password, st.session_state['users'][username]):
        st.session_state['logged_in'] = True
        return True
    return False

# Initialize database connection
db_file = 'your_database.db'
conn = create_connection(db_file)
create_table(conn)


def signup_form():
    with st.form("signup"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Signup")

        if submit:
            if signup(username, password, conn):  # Assuming signup() returns True on success
                st.success("Signup successful! Please login.")
                st.session_state['page'] = 'Login'  # Redirect to login page
            else:
                st.error("Username already exists or an error occurred.")



def validate_login(username, password, conn):
    """ Validate login credentials """
    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        user_data = cur.fetchone()
        if user_data:
            stored_password = user_data[0]
            return pbkdf2_sha256.verify(password, stored_password)
        return False
    except Exception as e:
        print(e)
        return False
def login_form():
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if validate_login(username, password, conn):
                st.session_state['logged_in'] = True  # Set logged_in to True
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect username or password.")


# Main app for pothole detection
def main_app():
    # Load YOLO model
    model = YOLO('model.pt')
    classnames = ['non_violence', 'violence']

    st.title('Welcome to the Human surveillence System')

    # Add options for user input: Image, Video, or Live Stream
    input_option = st.radio("Choose input type", ('Video', 'Live Stream'))
        # Logout button
    if st.button('Logout'):
        st.session_state['logged_in'] = False

    def process_frame(frame):
        frame = cv2.resize(frame, (640, 480))
        result = model(frame, stream=True)

        for info in result:
            boxes = info.boxes
            for box in boxes:
                confidence = box.conf[0]
                confidence = math.ceil(confidence * 100)
                Class = int(box.cls[0])
                if confidence > 50:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                    cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1 + 8, y1 + 100], scale=1.5, thickness=2)
                    if classnames[Class] == "violence":
                        s.sendmail("reddybhagyesh12@gmail.com", "reddybimbi@gmail.com", message)
                        playsound('3.wav')
                        st.write("Violence detected")
                    else:
                        st.write("Not a Violence detected")
        return frame

    
    
    if input_option == 'Video':
        uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi"])
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False) 
            tfile.write(uploaded_file.read())
            cap = cv2.VideoCapture(tfile.name)
            frameST = st.empty()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                processed_frame = process_frame(frame)
                frameST.image(processed_frame, channels="BGR", use_column_width=True)

            cap.release()

    elif input_option == 'Live Stream':
        st.write("Live Stream from Webcam")

        # Streamlit components for displaying webcam feed and processed frames
        frame_window = st.image([])
        frame_processed = st.image([])

        # Start capturing from the webcam
        cap = cv2.VideoCapture(0)  # 0 is typically the default webcam

        frame_count = 0  # Counter for unique button key

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame
            processed_frame = process_frame(frame)

            # Display the processed frames
            frame_processed.image(processed_frame, channels='BGR')

            # Break the loop if necessary, using a unique key for the button
            if st.button('Stop Streaming', key=f'stop_button_{frame_count}'):
                break

            frame_count += 1

        cap.release()


if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'  # Default page

# App routing
if not st.session_state.get('logged_in'):  # Check if user is not logged in
    st.sidebar.title("Navigation")
    # Use session state for controlling the current page
    option = st.sidebar.radio("Choose an option", ["Home", "Login", "Signup"], index=["Home", "Login", "Signup"].index(st.session_state['page']))

    if option == "Home":
        home_page()
    elif option == "Signup":
        signup_form()
    else:  # Login
        login_form()
else:
    main_app()  # User is logged in, display the main app


