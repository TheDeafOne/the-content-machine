import datetime
import os
import os.path as path
import sys

import pollinations as ai
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from groq import Groq
from moviepy.config import change_settings
from moviepy.editor import CompositeVideoClip, ImageClip, TextClip

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
    
    def generate_image(self, text):
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
            voice_id='7fbQ7yJuEo56rYjrYaEh',
        )
        audio = str.encode(response['audio_base64'])
        self._create_subs_srt(response["alignment"])
        save(audio, MP3_PATH)
   
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
            if char == " " or i == len(characters) - 1:
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
        subtitle_count = 1
        group = ""
        group_start_time = None
        group_end_time = None
        accumulated_duration = 0.0
        threshold = 1.0  # Minimum duration of 1 second

        for i, (word, start_time, end_time) in enumerate(parsed_subtitles.values()):
            # Start a new group if necessary
            if group == "":
                group_start_time = start_time

            # Add the word to the group
            group += word + " "

            # Accumulate the duration of this group
            accumulated_duration = end_time - group_start_time

            # If the duration exceeds the threshold, or it's the last word
            if accumulated_duration < threshold and i != len(parsed_subtitles):
                continue
            
            group_end_time = end_time

            srt_content.append(f'{subtitle_count}\n')
            srt_content.append(f'{self._format_time(group_start_time)} --> {self._format_time(group_end_time)}\n')
            srt_content.append(f'{group}\n\n')

            # Reset the group and duration for the next combination
            group = ""
            accumulated_duration = 0.0

        with open(SRT_PATH, 'w') as f:
            f.write(''.join(srt_content))
        

class VideoEditor:
    def edit(self):
        pass
        # subtitles = pysrt.open(SRT_PATH)

        # duration = subtitles[-1].end.seconds

        # # Load the image file and create a video from it (set the duration for how long the still image will be shown)
        # image = ImageClip(IMG_PATH, duration=duration)  # 10-second video

        # caption_clips = []
        # # Iterate through the subtitles and create text clips for each
        # for subtitle in subtitles:
        #     # Create a TextClip for each subtitle (caption)
        #     caption = TextClip(subtitle.text, fontsize=40, color='white')
        #     caption = caption.set_position(("center", "center")).set_start(subtitle.start.milliseconds).set_duration(subtitle.duration.milliseconds)

        #     # Append the caption clip to the list
        #     caption_clips.append(caption)

        # # Combine the image with the captions (overlay all caption clips on the image)
        # video_with_captions = CompositeVideoClip([image] + caption_clips)

        # # Write the final video to a file
        # video_with_captions.write_videofile(VIDEO_PATH, fps=24, codec="libx264")

if __name__ == "__main__":
    # ig = ImageGenerator()
    # response = ig.generate_image("A beautiful sunset over the mountains")
    n = Narrator()
    response = n.generate_voice_over("""A beautiful sunset over the sea""")
    # save(response, 'test.mp3')
    # ve = VideoEditor()
    # ve.edit()

    