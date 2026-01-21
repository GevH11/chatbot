from openai import OpenAI
from dotenv import load_dotenv
import os
from prompts import SYSTEM_PROMPT_ONE, SYSTEM_PROMPT_TWO

load_dotenv()
client = OpenAI()

# ---------------- SIMPLIFIED BOT ----------------
def run_bot(user_message, system_prompt):
    try:
        # createing prompt
        messages = [
            system_prompt,
            {"role": "user", "content": user_message}
        ]

        # call OpenAI
        resp = client.responses.create(
            model="gpt-5-nano",
            input=messages
        )
        return resp.output_text
    except Exception as e:
        print("ERROR in run_bot:", e)
        return f"[Error: {e}]"

def ChatbotOne(user_message):
    return run_bot(user_message, SYSTEM_PROMPT_ONE)

def ChatbotTwo(user_message):
    return run_bot(user_message, SYSTEM_PROMPT_TWO)

# ---------------- SIMULATION ----------------
def simulation(rounds=5):
    # Starting message from ChatbotOne
    output = ChatbotOne("Hello! Let's talk about something interesting.")
    print("Chatbot ONE SAYS:", output)

    for i in range(rounds):
        # ChatbotTwo to ChatbotOne
        output = ChatbotTwo(output)
        print("Chatbot TWO SAYS:", output)

        # ChatbotOne отвечает на ChatbotTwo
        output = ChatbotOne(output)
        print("Chatbot ONE SAYS:", output)

# ---------------- RUN ----------------
if __name__ == "__main__":
    simulation()