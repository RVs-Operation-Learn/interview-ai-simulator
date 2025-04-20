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
    return f"""{ROLE_TEMPLATES.get(role, '')}
{LEVEL_TEMPLATES.get(level, '')}
{DIFFICULTY_INSTRUCTIONS.get(difficulty, '')}
Your job is to ask technical interview questions one at a time and then evaluate the candidate's answers with a feedback and rate it on a scale of 1 to 10.
Be concise and professional. After 3 questions, end the interview with a summary.
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
    match = re.search(r"(\\d+(\\.\\d+)?)\\s*/\\s*10", feedback_text)
    #match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', feedback_text)
    if match:
        return float(match.group(1))
    else:
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
