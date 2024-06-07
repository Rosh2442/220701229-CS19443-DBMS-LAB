import streamlit as st
import mysql.connector
from datetime import datetime

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="roshini",
        database="courier_service"
    )

# User authentication
def authenticate_user(username, password):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE username=%s AND password=%s", (username, password ))
    user = cursor.fetchone()
    db.close()
    return user

# Sign up
def sign_up_user(username, password, email, phone_number, address, user_type):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Users (username, password, email, phone_number, address, user_type) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, password, email, phone_number, address, user_type)
    )
    db.commit()
    db.close()

# Home Page
def home():
    st.title("Courier Service Management System")
    choice = st.sidebar.selectbox("Login / signup", ["Login", "Signup"])

    
    if choice == "Signup":
        st.subheader("Create a new account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        address = st.text_area("Address")
        user_type = st.selectbox("User Type", ["Customer", "Admin"])
        
        if st.button("Signup"):
            sign_up_user(username, password, email, phone_number, address, user_type)
            st.success("You have successfully created an account. Please login now.")
    
    elif choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.session_state['user'] = user
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

# Place Order
def place_order():
    if 'user' not in st.session_state:
        st.warning("You need to login first")
        return

    st.subheader("Place a Courier Order")
    receiver_name = st.text_input("Receiver's Name")
    receiver_address = st.text_area("Receiver's Address")
    receiver_phone = st.text_input("Receiver's Phone Number")
    receiver_email = st.text_input("Receiver's Email")
    courier_type = st.text_input("Courier Type")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    precaution = st.text_area("Precaution (if any)")
    
    if st.button("Place Order"):
        db = get_db_connection()
        cursor = db.cursor()
        track_id = f"{st.session_state['user']['user_id']}{datetime.now()}"
        if receiver_name and receiver_address and receiver_phone :
            cursor.execute(
                "INSERT INTO Couriers (sender_id, receiver_name, receiver_address, receiver_phone, receiver_email, type, weight, precaution, track_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (st.session_state['user']['user_id'], receiver_name, receiver_address, receiver_phone, receiver_email, courier_type, weight, precaution, track_id)
            )
            db.commit()
            db.close()
            st.success(f"Order placed successfully! Your tracking ID is {track_id}")
            st.write(f"Your Tracking ID {track_id}")

# Track Courier
def track_courier():
    st.subheader("Track Your Courier")
    track_id = st.text_input("Enter Tracking ID")
    
    if st.button("Track"):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Couriers WHERE track_id=%s", (track_id,))
        courier = cursor.fetchone()
        db.close()
        if courier:
            st.write(f"Status: {courier['status']}")
            st.write(f"Receiver Name: {courier['receiver_name']}")
            st.write(f"Receiver Address: {courier['receiver_address']}")
            st.write(f"Receiver Phone: {courier['receiver_phone']}")
            st.write(f"Receiver Email: {courier['receiver_email']}")
        else:
            st.error("Invalid Tracking ID")

#admin fetch 
def admin_fetch():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM couriers")
    data = cursor.fetchall()
    for data in data :
        st.write(f"Courier ID :{data[0]}")
        st.write(f"Reciever  name  :{data[2]}")
        st.write(f"Reciever address :{data[3]}")
        st.write(f"Reciever mobile number :{data[4]}")
        st.write(f"courier type :{data[6]}")
        st.write(f"Order Status :{data[9]}")
        st.write(f"Tracking ID :{data[10]}")
        st.write("   ")
        st.write("   ")
        st.write("   ")




# Main function
def main():
    if 'user' in st.session_state:  
        st.sidebar.write(f"Welcome {st.session_state['user']['username']}")
        task = st.sidebar.selectbox("Select Task", ["Place Order", "Track Courier","Admin_Fetch", "Logout"])
        if task == "Admin_Fetch":
            st.header("ORDER DETAILS")
            admin_fetch()
        if task == "Place Order":
            place_order()
        elif task == "Track Courier":
            track_courier()
        elif task == "Logout":
            st.session_state.pop('user', None)
            st.experimental_rerun()
    else:
        home()

if __name__ == "__main__":
    main()
