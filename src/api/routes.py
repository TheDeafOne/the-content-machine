from flask import jsonify, request, send_file

from src.logic.creators import LLM, ImageGenerator, Narrator, VideoEditor
import src.logic.creators as creators

from . import api_bp

llm = LLM()
img_gen = ImageGenerator()
narrator = Narrator()
editor = VideoEditor()

@api_bp.post('/generate-text/')
def generate_text():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
    
    return jsonify(llm.complete(prompt)), 200  # TODO: manage errors

@api_bp.post('/generate-image-prompt/')
def generate_image_prompt():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
    
    return jsonify(llm.complete(prompt)), 200

@api_bp.post('/generate-image/')
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
        
    return jsonify(img_gen.generate_image(prompt)), 200

@api_bp.post('/generate-voice-over/')
def generate_voice_over():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({"error": "text is required."}), 400
    
    narrator.generate_voice_over(text)
    
    return send_file(creators.MP3_PATH), 200

@api_bp.post('/edit-video/')
def edit_video():
    editor.edit()
    return send_file(creators.VIDEO_PATH, 200)