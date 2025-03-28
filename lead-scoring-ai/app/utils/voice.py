import os
import requests
import speech_recognition as sr
from dotenv import load_dotenv
import hashlib
from pathlib import Path
from typing import Optional, Tuple
import wave
import contextlib
import tempfile

load_dotenv()

class VoiceService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'default')
        self.cache_dir = Path('voice_cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.recognizer = sr.Recognizer()
        
    def text_to_speech(self, text: str, voice_id: str = None) -> Optional[str]:
        """Convert text to speech using ElevenLabs API"""
        voice_id = voice_id or self.voice_id
        cache_key = hashlib.md5(f"{text}_{voice_id}".encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.wav"
        
        if cache_file.exists():
            return str(cache_file)
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            with open(cache_file, 'wb') as f:
                f.write(response.content)
                
            return str(cache_file)
        except Exception as e:
            print(f"Text-to-speech failed: {e}")
            return None

    def speech_to_text(self, audio_path: str) -> Tuple[Optional[str], Optional[float]]:
        """Convert speech to text using Google Speech Recognition"""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                duration = self._get_audio_duration(audio_path)
                
                if duration > 30:  # Limit to 30 seconds
                    return None, None
                    
                text = self.recognizer.recognize_google(audio)
                return text, duration
                
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return None, None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return None, None
        except Exception as e:
            print(f"Speech-to-text failed: {e}")
            return None, None

    def _get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file in seconds"""
        with contextlib.closing(wave.open(file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)

def generate_voice_response(prediction: dict) -> Optional[str]:
    """Generate voice response for prediction results"""
    service = VoiceService()
    
    if prediction.get('needs_human_review', False):
        text = f"Lead from {prediction.get('company', 'unknown')} scored {prediction['score']:.0%} and requires human review."
    else:
        text = f"Confident prediction for {prediction.get('company', 'unknown')}: {prediction['score']:.0%} conversion probability."
        
    return service.text_to_speech(text)

def process_voice_feedback(audio_path: str) -> Optional[str]:
    """Process voice feedback audio into text"""
    service = VoiceService()
    text, _ = service.speech_to_text(audio_path)
    return text
