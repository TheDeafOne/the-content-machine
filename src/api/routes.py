from flask import jsonify, request

from src.logic.creators import LLM, ImageGenerator

from . import api_bp

llm = LLM()
img_gen = ImageGenerator()

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



