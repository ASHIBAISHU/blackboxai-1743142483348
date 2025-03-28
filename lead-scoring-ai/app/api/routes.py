from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.prediction import LeadScorer
from app.utils.voice import generate_voice_response, process_voice_feedback
from app.utils.logging import log_request
from app.utils.auth import validate_feedback_token
import pandas as pd
import tempfile
import os

api_blueprint = Blueprint('api', __name__)
lead_scorer = LeadScorer()

@api_blueprint.route('/predict', methods=['POST'])
@jwt_required()
@log_request
def predict():
    try:
        data = request.get_json()
        
        # Make prediction
        prediction = lead_scorer.predict_lead(data)
        
        # Generate voice response if requested
        if request.args.get('voice', '').lower() == 'true':
            voice_response = generate_voice_response(prediction)
            prediction['voice_response'] = voice_response
        
        return jsonify(prediction), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_blueprint.route('/feedback', methods=['POST'])
@jwt_required()
@log_request
def feedback():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        data['user_id'] = user_id
        lead_scorer.process_feedback(data)
        return jsonify({'status': 'feedback received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_blueprint.route('/feedback/voice', methods=['POST'])
@jwt_required()
@log_request
def voice_feedback():
    try:
        # Get audio file and metadata
        audio_file = request.files.get('audio')
        prediction_id = request.form.get('prediction_id')
        user_id = get_jwt_identity()
        
        if not audio_file or not prediction_id:
            return jsonify({'error': 'Missing required data'}), 400

        # Save temp file
        temp_path = os.path.join(tempfile.gettempdir(), f"voice_feedback_{user_id}.wav")
        audio_file.save(temp_path)
        
        # Process voice feedback
        feedback_text = process_voice_feedback(temp_path)
        
        # Store feedback
        feedback_data = {
            'prediction_id': prediction_id,
            'feedback_text': feedback_text,
            'user_id': user_id,
            'voice_feedback_path': temp_path
        }
        lead_scorer.process_feedback(feedback_data)
        
        return jsonify({
            'status': 'voice feedback received',
            'transcription': feedback_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@api_blueprint.route('/voice/prediction', methods=['POST'])
@jwt_required()
@log_request
def prediction_voice():
    try:
        data = request.get_json()
        prediction = lead_scorer.predict_lead(data)
        
        # Generate voice file
        voice_file = generate_voice_response(prediction)
        
        return send_file(
            voice_file,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='prediction.wav'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_blueprint.route('/batch_predict', methods=['POST'])
@jwt_required()
@log_request
def batch_predict():
    try:
        data = request.get_json()
        leads = pd.DataFrame(data['leads'])
        results = []
        
        for _, lead in leads.iterrows():
            prediction = lead_scorer.predict_lead(lead.to_dict())
            results.append(prediction)
            
        return jsonify({'results': results}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_blueprint.route('/feedback/token', methods=['GET'])
def generate_feedback_token():
    try:
        prediction_id = request.args.get('prediction_id')
        if not prediction_id:
            return jsonify({'error': 'prediction_id required'}), 400
            
        token = validate_feedback_token(prediction_id)
        return jsonify({'token': token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
