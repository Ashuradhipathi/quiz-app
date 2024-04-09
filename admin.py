import json
from pymongo import MongoClient
import streamlit as st
import os

st.header('Enter the Questions', divider='rainbow')

# Connect to MongoDB
client = MongoClient(os.getenv('mongostr'), serverSelectionTimeoutMS=60000)
db = client["quiz_db"]
collection = db["quiz_collection"]
scores_collection = db["scores_collection"]  # Add scores_collection

# Initialize session state variables if they don't exist yet
if "current_question" not in st.session_state:
    st.session_state.questions = []
    st.session_state.right_answers = 0

def add_question():
    # Input box to enter the question
    question = st.text_input("Enter the question:")

    # Input box to enter the options
    options = st.text_input("Enter the options (comma-separated):")
    options_list = options.split(",")

    # Select box to choose the correct answer
    correct_answer = st.selectbox("Select the correct answer:", options_list)

    # Input box to enter the explanation
    explanation = st.text_area("Enter the explanation:")

    # Button to add the question to MongoDB
    if st.button("Add Question"):
        new_question = {
            "question": question,
            "options": options_list,
            "answer": correct_answer,
            "explanation": explanation,
        }
        collection.insert_one(new_question)
        st.success("Question added successfully!")

def show_scores():
    # Retrieve all documents from scores_collection
    scores = scores_collection.find()

    # Display the list of users along with their scores
    st.header("User Scores")
    for score in scores:
        st.write(f"Username: {score['username']}, Score: {score['score']}")

def delete_score(username):
    # Delete the document containing the user and their score
    scores_collection.delete_one({"username": username})
    st.success(f"Score for user {username} deleted successfully!")

# Create a 3-column layout for the question input fields
col1, col2, col3 = st.columns([1, 6, 1])

# Add the question input fields to the middle column
with col2:
    add_question()


st.header('LeaderBoard', divider='rainbow')
# Add a button to show the list of users and their scores
if st.button("Show Scores"):
    show_scores()

# Add a button to delete a user's score
st.header('Delete User!', divider='rainbow')
username = st.text_input("Enter the username to delete:")
if st.button("Delete"):
    delete_score(username)
