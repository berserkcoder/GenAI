from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
        api_key="AIzaSyC0CXoXPpCYmFZGO_p4iw6Vo5cRb29ituQ",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

system_prompt = ""
result = client.chat.completions.create(
    model="gemini-2.0-flash-lite",
    temperature = 1,
    messages=[
        { "role": "user", "content": "how to sort a list in python" } # Zero Shot Prompting
    ]
)

print(result.choices[0].message.content)