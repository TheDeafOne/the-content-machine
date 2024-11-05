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

            word += char

            # End of a word when a space is encountered or at the end of the list
            if not char.isalpha() or i == len(characters) - 1:
                if word.strip():  # Only add non-empty words
                    word_end_time = end_times[i]

                    # Append word and its timing
                    words.append(word.strip())
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
    # ve = VideoEditor()
    # ve.edit()

    debug_story = '''In a quiet village, nestled between the hills, there was an old, twisted tree known as the Whispering Oak. Every night, children heard strange murmurs when they passed by. The villagers said it was just the wind, but everyone knew better.

One chilly evening,'''

    debug_response={"characters": [" ", "I", "n", " ", "a", " ", "q", "u", "i", "e", "t", " ", "v", "i", "l", "l", "a", "g", "e", ",", " ", "n", "e", "s", "t", "l", "e", "d", " ", "b", "e", "t", "w", "e", "e", "n", " ", "t", "h", "e", " ", "h", "i", "l", "l", "s", ",", " ", "t", "h", "e", "r", "e", " ", "w", "a", "s", " ", "a", "n", " ", "o", "l", "d", ",", " ", "t", "w", "i", "s", "t", "e", "d", " ", "t", "r", "e", "e", " ", "k", "n", "o", "w", "n", " ", "a", "s", " ", "t", "h", "e", " ", "W", "h", "i", "s", "p", "e", "r", "i", "n", "g", " ", "O", "a", "k", ".", " ", "E", "v", "e", "r", "y", " ", "n", "i", "g", "h", "t", ",", " ", "c", "h", "i", "l", "d", "r", "e", "n", " ", "h", "e", "a", "r", "d", " ", "s", "t", "r", "a", "n", "g", "e", " ", "m", "u", "r", "m", "u", "r", "s", " ", "w", "h", "e", "n", " ", "t", "h", "e", "y", " ", "p", "a", "s", "s", "e", "d", " ", "b", "y", ".", " ", "T", "h", "e", " ", "v", "i", "l", "l", "a", "g", "e", "r", "s", " ", "s", "a", "i", "d", " ", "i", "t", " ", "w", "a", "s", " ", "j", "u", "s", "t", " ", "t", "h", "e", " ", "w", "i", "n", "d", ",", " ", "b", "u", "t", " ", "e", "v", "e", "r", "y", "o", "n", "e", " ", "k", "n", "e", "w", " ", "b", "e", "t", "t", "e", "r", ".", " ", "O", "n", "e", " ", "c", "h", "i", "l", "l", "y", " ", "e", "v", "e", "n", "i", "n", "g", ",", " "], "character_start_times_seconds": [0.0, 0.116, 0.174, 0.244, 0.29, 0.313, 0.383, 0.418, 0.499, 0.615, 0.697, 0.743, 0.789, 0.836, 0.882, 0.929, 0.987, 1.045, 1.115, 1.207, 1.242, 1.324, 1.393, 1.463, 1.521, 1.567, 1.625, 1.672, 1.695, 1.73, 1.765, 1.811, 1.858, 1.904, 1.962, 2.02, 2.055, 2.09, 2.113, 2.136, 2.159, 2.218, 2.252, 2.322, 2.392, 2.485, 2.659, 2.81, 3.019, 3.042, 3.077, 3.111, 3.146, 3.17, 3.204, 3.228, 3.251, 3.286, 3.332, 3.355, 3.402, 3.471, 3.646, 3.727, 3.796, 3.843, 3.878, 3.994, 4.052, 4.11, 4.18, 4.249, 4.331, 4.365, 4.412, 4.493, 4.574, 4.667, 4.76, 4.83, 4.876, 4.923, 4.957, 5.004, 5.05, 5.097, 5.132, 5.178, 5.236, 5.259, 5.283, 5.306, 5.375, 5.41, 5.457, 5.503, 5.573, 5.642, 5.7, 5.759, 5.817, 5.851, 5.875, 5.991, 6.118, 6.177, 6.327, 6.536, 7.233, 7.349, 7.396, 7.43, 7.477, 7.512, 7.581, 7.639, 7.709, 7.755, 7.79, 7.848, 7.872, 7.93, 7.988, 8.046, 8.104, 8.15, 8.208, 8.255, 8.301, 8.324, 8.382, 8.406, 8.452, 8.487, 8.533, 8.58, 8.626, 8.673, 8.766, 8.847, 8.916, 8.986, 9.044, 9.091, 9.137, 9.195, 9.242, 9.311, 9.358, 9.404, 9.462, 9.509, 9.543, 9.578, 9.601, 9.648, 9.671, 9.706, 9.729, 9.752, 9.776, 9.81, 9.88, 9.927, 9.996, 10.054, 10.112, 10.17, 10.194, 10.252, 10.321, 10.704, 10.913, 11.726, 11.784, 11.831, 11.854, 11.912, 11.947, 11.981, 12.028, 12.074, 12.132, 12.19, 12.249, 12.295, 12.341, 12.376, 12.411, 12.457, 12.504, 12.527, 12.562, 12.597, 12.62, 12.655, 12.69, 12.713, 12.748, 12.806, 12.852, 12.91, 12.968, 13.015, 13.061, 13.084, 13.108, 13.131, 13.189, 13.235, 13.351, 13.444, 13.595, 13.746, 14.025, 14.094, 14.153, 14.199, 14.245, 14.28, 14.327, 14.362, 14.396, 14.466, 14.536, 14.594, 14.64, 14.675, 14.71, 14.745, 14.779, 14.814, 14.872, 14.907, 14.965, 15.012, 15.07, 15.116, 15.232, 15.441, 16.951, 17.032, 17.125, 17.194, 17.264, 17.334, 17.403, 17.461, 17.508, 17.577, 17.647, 17.763, 17.879, 17.926, 17.972, 18.03, 18.1, 18.135, 18.251, 18.425], "character_end_times_seconds": [0.116, 0.174, 0.244, 0.29, 0.313, 0.383, 0.418, 0.499, 0.615, 0.697, 0.743, 0.789, 0.836, 0.882, 0.929, 0.987, 1.045, 1.115, 1.207, 1.242, 1.324, 1.393, 1.463, 1.521, 1.567, 1.625, 1.672, 1.695, 1.73, 1.765, 1.811, 1.858, 1.904, 1.962, 2.02, 2.055, 2.09, 2.113, 2.136, 2.159, 2.218, 2.252, 2.322, 2.392, 2.485, 2.659, 2.81, 3.019, 3.042, 3.077, 3.111, 3.146, 3.17, 3.204, 3.228, 3.251, 3.286, 3.332, 3.355, 3.402, 3.471, 3.646, 3.727, 3.796, 3.843, 3.878, 3.994, 4.052, 4.11, 4.18, 4.249, 4.331, 4.365, 4.412, 4.493, 4.574, 4.667, 4.76, 4.83, 4.876, 4.923, 4.957, 5.004, 5.05, 5.097, 5.132, 5.178, 5.236, 5.259, 5.283, 5.306, 5.375, 5.41, 5.457, 5.503, 5.573, 5.642, 5.7, 5.759, 5.817, 5.851, 5.875, 5.991, 6.118, 6.177, 6.327, 6.536, 7.233, 7.349, 7.396, 7.43, 7.477, 7.512, 7.581, 7.639, 7.709, 7.755, 7.79, 7.848, 7.872, 7.93, 7.988, 8.046, 8.104, 8.15, 8.208, 8.255, 8.301, 8.324, 8.382, 8.406, 8.452, 8.487, 8.533, 8.58, 8.626, 8.673, 8.766, 8.847, 8.916, 8.986, 9.044, 9.091, 9.137, 9.195, 9.242, 9.311, 9.358, 9.404, 9.462, 9.509, 9.543, 9.578, 9.601, 9.648, 9.671, 9.706, 9.729, 9.752, 9.776, 9.81, 9.88, 9.927, 9.996, 10.054, 10.112, 10.17, 10.194, 10.252, 10.321, 10.704, 10.913, 11.726, 11.784, 11.831, 11.854, 11.912, 11.947, 11.981, 12.028, 12.074, 12.132, 12.19, 12.249, 12.295, 12.341, 12.376, 12.411, 12.457, 12.504, 12.527, 12.562, 12.597, 12.62, 12.655, 12.69, 12.713, 12.748, 12.806, 12.852, 12.91, 12.968, 13.015, 13.061, 13.084, 13.108, 13.131, 13.189, 13.235, 13.351, 13.444, 13.595, 13.746, 14.025, 14.094, 14.153, 14.199, 14.245, 14.28, 14.327, 14.362, 14.396, 14.466, 14.536, 14.594, 14.64, 14.675, 14.71, 14.745, 14.779, 14.814, 14.872, 14.907, 14.965, 15.012, 15.07, 15.116, 15.232, 15.441, 16.951, 17.032, 17.125, 17.194, 17.264, 17.334, 17.403, 17.461, 17.508, 17.577, 17.647, 17.763, 17.879, 17.926, 17.972, 18.03, 18.1, 18.135, 18.251, 18.425, 18.715]}
    n = Narrator()
    response = n._create_subs_srt(debug_response)




    