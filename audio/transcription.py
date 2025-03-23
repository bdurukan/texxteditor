"""
Audio transcription services for the TextEditor.
"""

import requests
import tempfile
import os
import wave
import json
from tkinter import messagebox
import numpy as np

class TranscriptionService:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.last_error = None
        
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
            
            # Verify the audio file has content and isn't empty
            audio_file.seek(0, os.SEEK_END)
            file_size = audio_file.tell()
            audio_file.seek(0)
            
            if file_size == 0:
                raise ValueError("Audio file is empty")
            
            # Check if the file contains audio by reading a small sample
            sample_data = audio_file.read(1024)
            audio_file.seek(0)
            
            if len(sample_data) < 44:  # WAV header is at least 44 bytes
                raise ValueError("Audio file is too small or corrupted")
                
            # Prepare the multipart form data
            files = {
                'file': ('audio.wav', audio_file, 'audio/wav'),
                'model': (None, 'whisper-1'),
                'response_format': (None, 'json')  # Changed to JSON for better error handling
            }
            
            # Send request to OpenAI API
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                timeout=30  # Add timeout to prevent hanging
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
                self.last_error = error_msg
                raise ValueError(error_msg)
            
            # Extract transcript from response
            try:
                result = response.json()
                return result.get('text', '').strip()
            except json.JSONDecodeError:
                # Fall back to text response if not valid JSON
                return response.text.strip()
            
        except requests.RequestException as e:
            self.last_error = f"Network error: {str(e)}"
            raise ValueError(self.last_error)
            
    def process_audio_data(self, audio_frames, audio_format=None, channels=1, rate=44100, audio_device=None):
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
            
            # Check if audio contains actual sound
            if isinstance(audio_frames[0], np.ndarray):
                # For numpy arrays (like from sounddevice)
                audio_data = np.concatenate(audio_frames) if len(audio_frames) > 1 else audio_frames[0]
                rms = np.sqrt(np.mean(np.square(audio_data)))
                if rms < 0.001:  # Very low sound threshold
                    return ""
                    
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_filename = temp_wav.name
                
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(channels)
                    if audio_device and audio_format:
                        wf.setsampwidth(audio_device.get_sample_size(audio_format))
                    else:
                        wf.setsampwidth(2)  # Default to 16-bit if no format specified
                    wf.setframerate(rate)
                    
                    # Handle different types of audio data
                    if isinstance(audio_frames[0], bytes):
                        # PyAudio byte format
                        wf.writeframes(b''.join(audio_frames))
                    elif isinstance(audio_frames[0], np.ndarray):
                        # Sounddevice float32 format - convert to int16
                        audio_data = np.concatenate(audio_frames)
                        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                    else:
                        raise ValueError(f"Unsupported audio data format: {type(audio_frames[0])}")
                
            # Verify the file was created properly
            if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) < 44:
                raise ValueError("Failed to create valid WAV file")
                
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
            self.last_error = str(e)
            messagebox.showerror("Transcription Error", str(e))
            return ""
            
    def get_last_error(self):
        """Get the last error message."""
        return self.last_error