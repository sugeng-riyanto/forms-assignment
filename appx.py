import streamlit as st
import sqlite3
import uuid

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id TEXT PRIMARY KEY,
            user_name TEXT,
            user_signature TEXT,
            user_score INTEGER,
            second_user_name TEXT,
            second_user_signature TEXT,
            second_user_score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def generate_unique_link():
    unique_id = str(uuid.uuid4())
    return f"http://localhost:8501/?id={unique_id}", unique_id

def save_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO forms (id, user_name, user_signature, user_score, second_user_name, second_user_signature, second_user_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, data.get('user_name'), data.get('user_signature'), data.get('user_score'),
          data.get('second_user_name'), data.get('second_user_signature'), data.get('second_user_score')))
    conn.commit()
    conn.close()

def get_data(unique_id):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forms WHERE id = ?', (unique_id,))
    data = c.fetchone()
    conn.close()
    if data:
        return {
            'id': data[0],
            'user_name': data[1],
            'user_signature': data[2],
            'user_score': data[3],
            'second_user_name': data[4],
            'second_user_signature': data[5],
            'second_user_score': data[6]
        }
    return None

def update_data(unique_id, data):
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''
        UPDATE forms
        SET second_user_name = ?, second_user_signature = ?, second_user_score = ?
        WHERE id = ?
    ''', (data.get('second_user_name'), data.get('second_user_signature'), data.get('second_user_score'), unique_id))
    conn.commit()
    conn.close()

# Home page
def home():
    st.title("User Signature and Data Form")

    # Check if this is the second part of the form based on URL parameters
    query_params = st.query_params
    if "id" in query_params:
        unique_id = query_params["id"]
        if get_data(unique_id):
            second_user_form(unique_id)
        else:
            st.error("Invalid or expired link.")
    else:
        first_user_form()

def first_user_form():
    st.header("Step 1: Fill in your details, signature, and score")

    user_name = st.text_input("Your Name")
    user_signature = st.text_area("Your Signature (type here)")
    user_score = st.number_input("Your Score", min_value=0, max_value=100, step=1)

    if st.button("Generate Link for Second User"):
        if user_name and user_signature and user_score is not None:
            # Save the initial data
            initial_data = {
                "user_name": user_name,
                "user_signature": user_signature,
                "user_score": user_score,
                "second_user_name": None,
                "second_user_signature": None,
                "second_user_score": None
            }
            link, unique_id = generate_unique_link()
            save_data(unique_id, initial_data)
            
            st.success("Link generated! Share this link with the second user:")
            st.write(link)
        else:
            st.error("Please fill in all the fields.")

def second_user_form(unique_id):
    st.header("Step 2: Second User Completes the Form")

    user_data = get_data(unique_id)
    if user_data:
        st.write(f"Name of first user: {user_data['user_name']}")
        st.write(f"Signature of first user: {user_data['user_signature']}")
        st.write(f"Score of first user: {user_data['user_score']}")

        second_user_name = st.text_input("Your Name")
        second_user_signature = st.text_area("Your Signature (type here)")
        second_user_score = st.number_input("Your Score", min_value=0, max_value=100, step=1)

        if st.button("Submit"):
            if second_user_name and second_user_signature and second_user_score is not None:
                # Update second user's data
                user_data["second_user_name"] = second_user_name
                user_data["second_user_signature"] = second_user_signature
                user_data["second_user_score"] = second_user_score
                update_data(unique_id, user_data)
                
                st.success("Form completed and submitted successfully!")
                st.json(user_data)
            else:
                st.error("Please fill in all the fields.")
    else:
        st.error("Invalid or expired link.")

if __name__ == "__main__":
    init_db()
    home()
