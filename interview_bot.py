# interview_logic.py

import os
import openai
from dotenv import load_dotenv
import re

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Configuration Mapping ---
ROLE_TEMPLATES = {
    "Android Developer": "You are a technical interviewer for an Android Developer role.",
    "Data Scientist": "You are a technical interviewer for a Data Scientist role.",
    "AI Engineer": "You are a technical interviewer for an AI Engineer role."
}

LEVEL_TEMPLATES = {
    "Junior": "Ask simple and basic-level questions.",
    "Mid": "Ask intermediate-level technical questions.",
    "Senior": "Ask complex, architecture or design-level questions."
}

DIFFICULTY_INSTRUCTIONS = {
    "Easy": "Keep the questions easy and beginner-friendly.",
    "Medium": "Use moderately challenging questions.",
    "Hard": "Use difficult and tricky interview questions."
}

# --- Prompt Builder ---
def build_system_prompt(role, level, difficulty):
    return f"""You are a technical interviewer for a {role} role at {level} level.

🎯 Instructions:
- Ask **only one** interview question at a time.
- Do **not ask repeated questions**. Each time question has to be different.
- After each user answer, provide clear **feedback** and rate the response. Rating should be like 5/10.
- ✋ Do **not include the next question** in your feedback. 
- After 3 rounds, provide a brief summary if prompted.

🎯 Difficulty Level: {difficulty}
Ensure questions and feedback align with this level..
"""

# --- Interview Session Logic ---
def get_interview_question(conversation_history):
    #prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model
        messages=conversation_history  # This holds the conversation history
    )
    return response['choices'][0]['message']['content']

def extract_score(feedback_text):
    """
    Extracts a numeric score from feedback like '... I would rate your answer 8 out of 10.'
    """
    match = re.search(r'(\\b\\d{1,2}(\\.\\d+)?)(?=\\s*/\\s*10|\\s*out of\\s*10)', feedback_text, re.IGNORECASE)
    print(match)
    if match:
        score = float(match.group(1))
        if 0 <= score <= 10:
            return score
    return 0.0

def get_feedback_on_answer(conversation_history, user_answer):
    conversation_history.append({"role": "user", "content": user_answer})
    #prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model
        messages=conversation_history  # Pass the entire conversation so far
    )
    feedback = response['choices'][0]['message']['content']
    score = extract_score(feedback)
    return feedback, score, conversation_history
