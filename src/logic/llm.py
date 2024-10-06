import os

from groq import Groq

from config import LLM_API_KEY


class LLM:
    def __init__(self):
        self.llm = Groq(api_key=LLM_API_KEY)

    def complete(self, text):
        response = self.llm.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
        )
        return response.choices[0].message.content

if __name__ == "__main__":
    llm = LLM()
    response = llm.complete("What is the meaning of life?")
    print(response)
    