from flask import jsonify
from src.logic import creator
from . import api_bp


@api_bp.get('/generate_text/')
def get_info():
    response = creator.generate_content()
    return jsonify(response)  # Send JSON response


