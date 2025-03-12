"""
Audio recording functionality for the TextEditor.
Modified to work with the new MS Word-like interface
"""

import threading
import pyaudio
import wave
import tempfile
import time
import sounddevice as sd
import numpy as np
import keyboard
from tkinter import messagebox
import os
from .transcription import TranscriptionService

class AudioRecorder:
    def __init__(self, settings_manager, status_callback=None, transcription_callback=None):
        self.settings_manager = settings_manager
        self.status_callback = status_callback
        self.transcription_callback = transcription_callback
        self.transcription_service = TranscriptionService(settings_manager)
        
        # Initialize recording variables
        self.is_recording = False
        self.recording_thread = None
        self.audio_frames = []
        
        # Audio configuration
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        
    def update_status(self, message):
        """Update the status message if callback is provided."""
        if self.status_callback:
            self.status_callback(message)
            
    def start_microphone_transcription(self):
        """Start recording from the microphone for transcription."""
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            messagebox.showerror("Error", "Please configure your OpenAI API key first")
            return False
        
        if self.is_recording:
            return False
            
        self.update_status("Recording... (Hold the transcription key)")
        self.is_recording = True
        self.audio_frames = []
        
        # Start recording in a new thread
        self.recording_thread = threading.Thread(target=self.record_microphone)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        return True
        
    def record_microphone(self):
        """Record audio from the microphone."""
        stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        # Record audio while key is held
        try:
            while keyboard.is_pressed(self.settings_manager.get_shortcuts()["transcribe"]):
                data = stream.read(self.chunk)
                self.audio_frames.append(data)
                time.sleep(0.01)  # Small delay to reduce CPU usage
        finally:
            stream.stop_stream()
            stream.close()
            self.is_recording = False
            
            if self.audio_frames:
                self.update_status("Transcribing audio...")
                self.transcribe_audio()
            else:
                self.update_status("Recording cancelled")
                
    def transcribe_audio(self):
        """Transcribe recorded audio."""
        try:
            # Save the recorded audio to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_filename = temp_wav.name
                
                wf = wave.open(temp_filename, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))
                wf.close()
            
            # Send to OpenAI for transcription
            with open(temp_filename, "rb") as audio_file:
                transcript = self.transcription_service.transcribe_with_openai(audio_file)
                
            # Add the transcribed text via callback
            if transcript:
                if self.transcription_callback:
                    self.transcription_callback(transcript + " ")
                self.update_status("Transcription completed")
            else:
                self.update_status("No speech detected")
                
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
        except Exception as e:
            self.update_status(f"Transcription error: {str(e)}")
            messagebox.showerror("Transcription Error", str(e))
            
    def start_system_audio_capture(self):
        """Start capturing system audio."""
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            messagebox.showerror("Error", "Please configure your OpenAI API key first")
            return False
        
        if self.is_recording:
            return False
            
        self.update_status("Recording system audio... (Release the key to stop)")
        self.is_recording = True
        self.audio_frames = []
        
        # Start recording in a new thread
        self.recording_thread = threading.Thread(target=self.record_system_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        return True
        
    def record_system_audio(self):
        """Record system audio output."""
        try:
            # Get list of audio devices
            devices = sd.query_devices()
            
            # Look for system audio output device
            device_id = None
            for i, device in enumerate(devices):
                if 'Stereo Mix' in device['name'] or 'What U Hear' in device['name'] or 'output' in device['name'].lower():
                    device_id = i
                    break
            
            # If no specific system audio device found, use default
            if device_id is None:
                self.update_status("Warning: Using default device. May not capture system audio.")
            
            # Configure stream parameters
            channels = 2
            sample_rate = 44100
            
            # Open the input stream
            stream = sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                device=device_id,
                callback=self.audio_callback
            )
            
            # Start recording
            with stream:
                # Record while key is held
                while keyboard.is_pressed(self.settings_manager.get_shortcuts()["system_audio"]):
                    time.sleep(0.01)  # Small delay to reduce CPU usage
                    
            # Key was released, stop recording
            self.is_recording = False
            
            if self.audio_frames:
                self.update_status("Transcribing system audio...")
                
                # Process audio in a separate thread
                process_thread = threading.Thread(target=self.process_system_audio, 
                                                 args=(channels, sample_rate))
                process_thread.daemon = True
                process_thread.start()
            else:
                self.update_status("System audio recording cancelled")
                
        except Exception as e:
            self.is_recording = False
            self.update_status(f"System audio recording error: {str(e)}")
            
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if self.is_recording:
            self.audio_frames.append(indata.copy())
            
    def process_system_audio(self, channels, sample_rate):
        """Process system audio and send for transcription."""
        try:
            # Skip if no audio was captured
            if not self.audio_frames:
                self.update_status("No audio captured")
                return
                
            # Convert to a single numpy array
            audio_data = np.concatenate(self.audio_frames)
            
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_filename = temp_wav.name
                
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                    
            # Send to OpenAI for transcription
            with open(temp_filename, "rb") as audio_file:
                transcript = self.transcription_service.transcribe_with_openai(audio_file)
                
            # Add the transcribed text
            if transcript:
                if self.transcription_callback:
                    self.transcription_callback(transcript + " ")
                self.update_status("System audio transcription completed")
            else:
                self.update_status("No speech detected in system audio")
                
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
        except Exception as e:
            self.update_status(f"System audio processing error: {str(e)}")
            messagebox.showerror("Transcription Error", str(e))