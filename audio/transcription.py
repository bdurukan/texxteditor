"""
Audio transcription services for the TextEditor.
"""

import requests
import tempfile
import os
import wave
from tkinter import messagebox

class TranscriptionService:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        
    def transcribe_with_openai(self, audio_file):
        """
        Transcribe audio file using OpenAI's API.
        
        Args:
            audio_file: An open file object containing audio data.
            
        Returns:
            str: Transcribed text or empty string if transcription failed.
        """
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            raise ValueError("API key not configured")
            
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            # Reset file pointer to the beginning
            audio_file.seek(0)
            
            # Prepare the multipart form data
            files = {
                'file': ('audio.wav', audio_file, 'audio/wav'),
                'model': (None, 'whisper-1'),
                'response_format': (None, 'text')
            }
            
            # Send request to OpenAI API
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = f"API Error: {error_data['error']['message']}"
                except:
                    pass
                raise ValueError(error_msg)
            
            # Return the transcribed text
            return response.text.strip()
            
        except requests.RequestException as e:
            raise ValueError(f"Network error: {str(e)}")
            
    def process_audio_data(self, audio_frames, audio_format, channels, rate, audio_device=None):
        """
        Process audio data and send for transcription.
        
        Args:
            audio_frames: List of audio data frames.
            audio_format: Format of the audio data.
            channels: Number of audio channels.
            rate: Sample rate of the audio.
            audio_device: Audio device used for recording.
            
        Returns:
            str: Transcribed text or empty string if processing failed.
        """
        try:
            # Skip if no audio was captured
            if not audio_frames:
                return ""
                
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_filename = temp_wav.name
                
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(audio_device.get_sample_size(audio_format) if audio_device else 2)
                    wf.setframerate(rate)
                    wf.writeframes(b''.join(audio_frames))
                
            # Send to OpenAI for transcription
            with open(temp_filename, "rb") as audio_file:
                transcript = self.transcribe_with_openai(audio_file)
                
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
            return transcript
                
        except Exception as e:
            messagebox.showerror("Transcription Error", str(e))
            return ""