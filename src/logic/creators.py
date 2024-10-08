import os
import os.path as path
import sys

import pollinations as ai
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from groq import Groq

from config import LLM_API_KEY, NARRATION_API_KEY

TMP_DIRECTORY = path.join(path.split(path.abspath(__file__))[0], 'tmp')

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
        response.choices
        return self.parse_groq_response(response)
    

    def parse_groq_response(self, response):
        return [
            {
                "text": choice.message.content,
                "logprobs": choice.logprobs,
                "finish_reason": choice.finish_reason,
                "index": choice.index,
            }
            for choice in response.choices
        ]
    

class ImageGenerator:
    def __init__(self):
        self.image_generator = ai.ImageModel()
    
    def generate_image(self, text):
        response = self.image_generator.generate(
            prompt=text,
            model='flux',
            width=768,
            height=768,
            seed=42,
            nologo=True
        )
        return {
            "prompt": text,
            "url": response.url,
        }
    
class Narrator:
    def __init__(self):
        self.narrator = ElevenLabs(api_key=NARRATION_API_KEY, timeout=None)
        self.narration_mp3_path = path.join(TMP_DIRECTORY, 'tmp.mp3')
    
    def generate_voice_over(self, text):
        print('generating narration..')
        response = self.narrator.generate(
            text=text,
            voice="John Doe - Intimate",
        )
        save(response, self.narration_mp3_path)
   
    def delete_voice_over(self):
        os.remove(self.narration_mp3_path)

if __name__ == "__main__":
    # ig = ImageGenerator()
    # response = ig.generate_image("A beautiful sunset over the mountains")
    n = Narrator()
    response = n.generate_voice_over("A beautiful sunset over the mountains")
    # save(response, 'test.mp3')

    