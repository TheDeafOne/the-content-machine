import os

from dotenv import load_dotenv

load_dotenv()

RELOAD_DB = os.getenv("RELOAD_DB")
LLM_API_KEY = os.getenv("LLM_API_KEY")
DEBUG_MODE = os.getenv("DEBUG_MODE")
NARRATION_API_KEY = os.getenv("NARRATION_API_KEY")
FFMPEG_LOCATION = os.getenv("FFMPEG_LOCATION")
IMAGE_MAGICK_LOCATION = os.getenv("IMAGE_MAGICK_LOCATION")