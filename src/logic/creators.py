import os
import os.path as path
import sys
import datetime


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
        self.narration_srt_path = path.join(TMP_DIRECTORY, 'tmp_subs.srt')
    
    def generate_voice_over(self, text):
        print('generating narration...')
        response = self.narrator.text_to_speech.convert_with_timestamps(
            text=text,
            voice_id='7fbQ7yJuEo56rYjrYaEh',
        )
        audio = str.encode(response['audio_base64'])
        self._create_subs_srt(response["alignment"])
        save(audio, self.narration_mp3_path)
   
    def delete_voice_over(self):
        os.remove(self.narration_mp3_path)

    
    def _format_time(self, seconds):
        td = datetime.timedelta(seconds=seconds)
        total_seconds = td.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = (seconds % 1) * 1000
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"
    
    def _create_subs_srt(self, subtitles):
        characters = subtitles['characters']
        start_times = subtitles['character_start_times_seconds']
        end_times = subtitles['character_end_times_seconds']

        # Initialize variables
        srt_content = ""
        word = ""
        word_start_time = None
        word_end_time = None
        subtitle_count = 1

        for i in range(len(characters)):
            char = characters[i]
            
            # Start of a new word
            if word == "":
                word_start_time = start_times[i]

            word += char
            
            # End of the word when a space is encountered or end of character list
            if char == " " or i == len(characters) - 1:
                if word.strip():  # Only create subtitles for non-empty words
                    word_end_time = end_times[i]

                    # Format SRT entry
                    srt_content += f"{subtitle_count}\n"
                    srt_content += f"{self._format_time(word_start_time)} --> {self._format_time(word_end_time)}\n"
                    srt_content += word.strip() + "\n\n"

                    # Increment subtitle counter and reset the word
                    subtitle_count += 1

                # Reset word
                word = ""

        # Write SRT content to file
        with open(self.narration_srt_path, "w") as f:
            f.write(srt_content)


if __name__ == "__main__":
    # ig = ImageGenerator()
    # response = ig.generate_image("A beautiful sunset over the mountains")
    n = Narrator()
    response = n.generate_voice_over("""A beautiful sunset over the sea""")
    # save(response, 'test.mp3')

    