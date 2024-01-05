import json
from pymongo import MongoClient
import streamlit as st

st.header('Time for :blue[Quiz] :sunglasses:')
# # Connect to MongoDB
client = MongoClient(os.getenv('mongostr'), serverSelectionTimeoutMS=60000)
db = client["quiz_db"]
collection = db["quiz_collection"]
scores_collection = db["scores_collection"]  # New collection for storing scores

username = st.sidebar.text_input("Enter your username:")
# Input box to enter the username
def show_scores():
    # Retrieve all documents from scores_collection in descending order of score
    scores = scores_collection.find().sort("score", -1)

    # Display the list of users along with their scores
    st.sidebar.header("Leaderboard")
    for score in scores:
        st.sidebar.write(f"Username: {score['username']}, Score: {score['score']}")


show_scores()

# Retrieve the questions from the MongoDB database
questions = list(collection.find())

# Initialize session state variables if they don't exist yet
if "current_question" not in st.session_state:
    st.session_state.answers = {}
    st.session_state.current_question = 0
    st.session_state.right_answers = 0
    st.session_state.wrong_answers = 0

def display_question():
    # Handle first case
    if len(questions) == 0:
        st.error("No questions available.")
        return

    # Disable the submit button if the user has already answered this question
    submit_button_disabled = st.session_state.current_question in st.session_state.answers

    # Get the current question from the questions list
    question = questions[st.session_state.current_question]

    # Display the question prompt
    st.write(f"{st.session_state.current_question + 1}. {question['question']}")

    # Use an empty placeholder to display the radio button options
    options = st.empty()

    # Display the radio button options and wait for the user to select an answer
    user_answer = options.radio("Your answer:", question["options"], key=st.session_state.current_question)

    # Display the submit button and disable it if necessary
    submit_button = st.button("Submit", disabled=submit_button_disabled)

    # If the user has already answered this question, display their previous answer
    if st.session_state.current_question in st.session_state.answers:
        index = st.session_state.answers[st.session_state.current_question]
        options.radio(
            "Your answer:",
            question["options"],
            key=float(st.session_state.current_question),
            index=index,
        )

    # If the user clicks the submit button, check their answer and show the explanation
    if submit_button:
        # Record the user's answer in the session state
        st.session_state.answers[st.session_state.current_question] = question["options"].index(user_answer)

        # Check if the user's answer is correct and update the score
        if user_answer == question["answer"]:
            st.write("Correct!")
            st.session_state.right_answers += 1
        else:
            st.write(f"Sorry, the correct answer was {question['answer']}.")
            st.session_state.wrong_answers += 1

        # Show an expander with the explanation of the correct answer
        with st.expander("Explanation"):
            st.write(question["explanation"])

        # Update the student's score in MongoDB
        student_score = {
            "username": username,
            "score": st.session_state.right_answers,
        }
        scores_collection.update_one({"username": username}, {"$set": student_score}, upsert=True)

    # Display the current score
    st.write(f"Right answers: {st.session_state.right_answers}")
    st.write(f"Wrong answers: {st.session_state.wrong_answers}")

# Define a function to go to the next question
def next_question():
    # Move to the next question in the questions list
    st.session_state.current_question += 1

    # If we've reached the end of the questions list, loop back to the first question
    if st.session_state.current_question > len(questions) - 1:
        st.session_state.current_question = 0

# Define a function to go to the previous question
def prev_question():
    # Move to the previous question in the questions list
    if st.session_state.current_question > 0:
        st.session_state.current_question -= 1

# Create a 3-column layout for the Prev/Next buttons and the question display
col1, col2, col3 = st.columns([1, 6, 1])

# Add a Prev button to the left column that goes to the previous question
with col1:
    if col1.button("Prev"):
        prev_question()

# Add a Next button to the right column that goes to the next question
with col3:
    if col3.button("Next"):
        next_question()

# Display the actual quiz question
with col2:
    display_question()

