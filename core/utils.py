import openai, os
from dotenv import load_dotenv
load_dotenv()

def ask_openai_math_solver(question):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a math teacher. Solve math problems step by step."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message['content'].strip()
