import datetime
import os
import os.path as path
import sys
import base64
import json

import pollinations as ai
from elevenlabs.client import ElevenLabs
from groq import Groq
from moviepy.config import change_settings
from moviepy.editor import CompositeVideoClip, ImageClip, TextClip, AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

from config import (FFMPEG_LOCATION, IMAGE_MAGICK_LOCATION, LLM_API_KEY,
                    NARRATION_API_KEY)

change_settings({"FFMPEG_BINARY": FFMPEG_LOCATION, "IMAGEMAGICK_BINARY": IMAGE_MAGICK_LOCATION})

TMP_DIRECTORY = path.join(path.split(path.abspath(__file__))[0], 'tmp')

MP3_PATH = path.join(TMP_DIRECTORY, 'tmp.mp3')
SRT_PATH = path.join(TMP_DIRECTORY, 'tmp_subs.srt')
IMG_PATH = path.join(TMP_DIRECTORY, 'tmp_img.png')
VIDEO_PATH = path.join(TMP_DIRECTORY, 'tmp_video.mp4')

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
    
    def generate_image(self, text): #TODO: update this to latest version
        response = self.image_generator.generate(
            prompt=text,
            model='flux',
            width=768,
            height=768,
            seed=42,
            nologo=True
        )
        # save img
        with open(IMG_PATH, 'wb') as handler:
            handler.write(response.content)
        return {
            "prompt": text,
            "url": response.url,
        }
    
class Narrator:
    def __init__(self):
        self.narrator = ElevenLabs(api_key=NARRATION_API_KEY, timeout=None)
        
    def generate_voice_over(self, text):
        print('generating narration...')
        response = self.narrator.text_to_speech.convert_with_timestamps(
            text=text,
            voice_id='7fbQ7yJuEo56rYjrYaEh', # TODO: make this a ui customizable thing
        )
        with open('debug_narration.txt', 'w') as f:
            f.write(json.dumps(response))
        audio = str.encode(response['audio_base64'])
        audio_data = base64.b64decode(audio)

        self._create_subs_srt(response["alignment"])
        # Save the audio data to a file
        with open(MP3_PATH, "wb") as f:
            f.write(audio_data)
   
    def delete_voice_over(self):
        os.remove(MP3_PATH)

    
    def _format_time(self, seconds):
        td = datetime.timedelta(seconds=seconds)
        total_seconds = td.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = (seconds % 1) * 1000
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"
    
    def _parse_response_subtitles(self, subtitles):
        characters = subtitles['characters']
        start_times = subtitles['character_start_times_seconds']
        end_times = subtitles['character_end_times_seconds']

        words = []
        word_start_times = []
        word_end_times = []

        word = ""
        word_start_time = None
        word_end_time = None

        for i in range(len(characters)):
            char = characters[i]

            # Start a new word if necessary
            if word == "":
                word_start_time = start_times[i]

            word = (word + (char if char.isalpha() else ''))
            # End of a word when a space is encountered or at the end of the list
            if not char.isalpha() or i == len(characters) - 1:
                if word:  # Only add non-empty words
                    word_end_time = end_times[i]

                    # Append word and its timing
                    words.append(word)
                    word_start_times.append(word_start_time)
                    word_end_times.append(word_end_time)

                # Reset the word
                word = ""

        return {
            'words': words,
            'word_start_times': word_start_times,
            'word_end_times': word_end_times
        }
    
    def _create_subs_srt(self, subtitles):
        parsed_subtitles = self._parse_response_subtitles(subtitles)
        srt_content = []
        for i, (word, start_time, end_time) in enumerate(zip(*parsed_subtitles.values())):
        
            srt_content.append(f'{i+1}\n')
            srt_content.append(f'{self._format_time(start_time)} --> {self._format_time(end_time)}\n')
            srt_content.append(f'{word.strip().replace('.','')}\n\n')

        with open(SRT_PATH, 'w') as f:
            f.write(''.join(srt_content))
        

class VideoEditor:
    def edit(self):
        # subtitles = pysrt.open(SRT_PATH)

        # duration = subtitles[-1].end.seconds

        # Load the image file and create a video from it (set the duration for how long the still image will be shown)
        audio_clip = AudioFileClip(MP3_PATH)
        image = ImageClip(IMG_PATH, duration=audio_clip.duration)  # 10-second video
        generator = lambda txt: TextClip(
            txt, # TODO: make all this font shit customizable via the ui
            font="arial", 
            fontsize=80, 
            color="white", 
            method='caption', 
            size=image.size,
            # stroke_width=10,
            # method='label'
        )
        sub_clip = SubtitlesClip(SRT_PATH, generator)
        # Combine the image with the captions (overlay all caption clips on the image)
        video_with_captions = CompositeVideoClip([image, sub_clip])
        video_with_captions: CompositeVideoClip = video_with_captions.set_audio(audio_clip)
        # Write the final video to a file
        video_with_captions.write_videofile(VIDEO_PATH, fps=24)

if __name__ == "__main__":
    # ig = ImageGenerator()
    # response = ig.generate_image("A beautiful sunset over the mountains")
    # save(response, 'test.mp3')
    ve = VideoEditor()
    ve.edit()
    # n = Narrator()
    # response = n._create_subs_srt(debug_value)
    




    