"""
System audio capture functionality for the TextEditor.
Specializes in capturing system audio from sources like YouTube videos,
Zoom conferences, and other media for transcription.
"""

import threading
import time
import tempfile
import os
import wave
import numpy as np
import sounddevice as sd
from tkinter import messagebox
import keyboard
import queue

class SystemAudioCapture:
    def __init__(self, settings_manager, transcription_service, status_callback=None, 
                 text_callback=None, continuous_mode=False):
        """
        Initialize the SystemAudioCapture.
        
        Args:
            settings_manager: Settings manager instance to get API key and other settings
            transcription_service: Service to handle transcription of audio
            status_callback: Callback to update status messages
            text_callback: Callback to add transcribed text to the editor
            continuous_mode: If True, enables continuous transcription mode
        """
        self.settings_manager = settings_manager
        self.transcription_service = transcription_service
        self.status_callback = status_callback
        self.text_callback = text_callback
        self.continuous_mode = continuous_mode
        
        # Recording state
        self.is_recording = False
        self.is_paused = False
        self.recording_thread = None
        self.audio_frames = []
        self.audio_device_id = None
        
        # Audio configuration
        self.channels = 2  # Stereo for better quality
        self.sample_rate = 44100  # Standard quality
        self.chunk_duration = 10  # Seconds per chunk for continuous mode
        
        # Processing queue for continuous mode
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        
        # Find available audio devices
        self._find_audio_devices()
        
    def _find_audio_devices(self):
        """Scan and identify system audio devices."""
        try:
            self.update_status("Scanning for system audio devices...")
            devices = sd.query_devices()
            
            # Look for likely system audio output devices
            loopback_names = [
                'stereo mix', 'what u hear', 'wave out', 'output', 'monitor', 
                'loopback', 'wasapi', 'audio interface', 'system', 'cable'
            ]
            
            # First look for dedicated loopback devices
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                if any(name in device_name for name in loopback_names) and device.get('max_input_channels', 0) > 0:
                    self.audio_device_id = i
                    self.update_status(f"Found system audio device: {device['name']}")
                    return
                    
            # If no dedicated loopback device is found, look for a default input
            for i, device in enumerate(devices):
                if device.get('max_input_channels', 0) > 0 and device.get('hostapi', 0) == 0:
                    self.audio_device_id = i
                    self.update_status(f"Using default input device: {device['name']}")
                    return
                    
            # No suitable device found
            self.update_status("Warning: No suitable system audio device found")
            self.audio_device_id = None
            
        except Exception as e:
            self.update_status(f"Error scanning audio devices: {str(e)}")
            self.audio_device_id = None
            
    def update_status(self, message):
        """Update status message if callback is provided."""
        if self.status_callback:
            self.status_callback(message)
            
    def start_capture(self, shortcut_key=None, duration=None):
        """
        Start capturing system audio.
        
        Args:
            shortcut_key: Keyboard shortcut to hold for recording
            duration: Maximum recording duration in seconds (None for manual stop)
            
        Returns:
            bool: True if capture started successfully, False otherwise
        """
        # Check for API key
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            messagebox.showerror("Error", "Please configure your OpenAI API key first")
            return False
            
        # Check if already recording
        if self.is_recording:
            return False
            
        # Reset recording state
        self.is_recording = True
        self.is_paused = False
        self.audio_frames = []
        
        # Update status
        key_message = f" (Hold '{shortcut_key}' key)" if shortcut_key else ""
        self.update_status(f"Recording system audio{key_message}...")
        
        # Start recording in a new thread
        self.recording_thread = threading.Thread(
            target=self._record_audio,
            args=(shortcut_key, duration)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # If in continuous mode, also start the processing thread
        if self.continuous_mode:
            self.processing_thread = threading.Thread(
                target=self._process_continuous_audio
            )
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
        return True
        
    def stop_capture(self):
        """Stop capturing system audio."""
        if not self.is_recording:
            return False
            
        self.is_recording = False
        self.update_status("Stopping system audio capture...")
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
            
        return True
        
    def pause_capture(self):
        """Pause system audio capture."""
        if not self.is_recording or self.is_paused:
            return False
            
        self.is_paused = True
        self.update_status("System audio capture paused")
        return True
        
    def resume_capture(self):
        """Resume system audio capture after pausing."""
        if not self.is_recording or not self.is_paused:
            return False
            
        self.is_paused = False
        self.update_status("System audio capture resumed")
        return True
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function for audio data from sounddevice."""
        if status:
            self.update_status(f"Audio callback status: {status}")
            
        if self.is_recording and not self.is_paused:
            # Add audio data to frames or queue depending on mode
            if self.continuous_mode:
                # Add to processing queue
                self.audio_queue.put(indata.copy())
            else:
                # Add to frames collection
                self.audio_frames.append(indata.copy())
    
    def _record_audio(self, shortcut_key=None, duration=None):
        """Record system audio in a background thread."""
        try:
            # Configure stream parameters
            stream_settings = {
                'samplerate': self.sample_rate,
                'channels': self.channels,
                'callback': self._audio_callback,
                'dtype': 'float32'
            }
            
            # Use device ID if available
            if self.audio_device_id is not None:
                stream_settings['device'] = self.audio_device_id
                
            # Open the input stream
            with sd.InputStream(**stream_settings):
                # Calculate end time if duration specified
                end_time = time.time() + duration if duration else None
                
                if shortcut_key:
                    # Record while key is held
                    while keyboard.is_pressed(shortcut_key) and self.is_recording:
                        # Check duration limit if specified
                        if end_time and time.time() > end_time:
                            break
                        time.sleep(0.01)  # Small delay to reduce CPU usage
                else:
                    # Record until manually stopped
                    while self.is_recording:
                        # Check duration limit if specified
                        if end_time and time.time() > end_time:
                            break
                        time.sleep(0.1)  # Larger delay for less frequent checks
                        
            # Recording has stopped
            self.is_recording = False
            
            # Process audio if we have data and not in continuous mode
            if self.audio_frames and not self.continuous_mode:
                self.update_status("Processing system audio...")
                self._process_audio()
            elif not self.audio_frames:
                self.update_status("No audio captured")
                
        except Exception as e:
            self.is_recording = False
            error_msg = str(e)
            self.update_status(f"System audio recording error: {error_msg}")
            messagebox.showerror("System Audio Error", error_msg)
                
    def _process_audio(self):
        """Process and transcribe recorded audio."""
        try:
            # Skip if no audio was captured
            if not self.audio_frames:
                self.update_status("No audio data to process")
                return
                
            # Convert to a single numpy array
            audio_data = np.concatenate(self.audio_frames)
            
            # Check if audio contains actual sound (not just silence)
            # Calculate RMS amplitude
            rms = np.sqrt(np.mean(np.square(audio_data)))
            if rms < 0.001:  # Very low amplitude threshold
                self.update_status("Audio appears to be silent, skipping transcription")
                return
                
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_filename = temp_wav.name
                
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                    
            # Send to transcription service
            with open(temp_filename, "rb") as audio_file:
                self.update_status("Transcribing audio...")
                transcript = self.transcription_service.transcribe_with_openai(audio_file)
                
            # Add the transcribed text to the editor
            if transcript:
                if self.text_callback:
                    self.text_callback(transcript + " ")
                self.update_status("System audio transcription completed")
            else:
                self.update_status("No speech detected in system audio")
                
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"System audio processing error: {error_msg}")
            messagebox.showerror("Transcription Error", error_msg)
            
    def _process_continuous_audio(self):
        """Process audio chunks continually for real-time transcription."""
        chunk_frames = []
        last_process_time = time.time()
        
        while self.is_recording or not self.audio_queue.empty():
            # Process all available frames up to our chunk duration
            try:
                # Get frames from queue with a timeout
                frame = self.audio_queue.get(timeout=0.5)
                chunk_frames.append(frame)
                
                # Check if we've reached the chunk duration
                chunk_duration = len(chunk_frames) * (len(frame) / self.sample_rate / self.channels)
                current_time = time.time()
                time_since_last = current_time - last_process_time
                
                # Process if we have enough data or enough time has passed
                if chunk_duration >= self.chunk_duration or time_since_last >= 30:
                    if chunk_frames:
                        # Process this chunk
                        self._process_chunk(chunk_frames)
                        chunk_frames = []  # Reset for next chunk
                        last_process_time = current_time
                        
            except queue.Empty:
                # No more frames in queue, wait a bit
                time.sleep(0.1)
                
        # Process any remaining frames
        if chunk_frames:
            self._process_chunk(chunk_frames)
            
    def _process_chunk(self, chunk_frames):
        """Process and transcribe a chunk of audio frames."""
        try:
            # Convert frames to a single array
            audio_data = np.concatenate(chunk_frames)
            
            # Check if audio contains actual sound (not just silence)
            rms = np.sqrt(np.mean(np.square(audio_data)))
            if rms < 0.001:  # Very low amplitude threshold
                return  # Skip silent audio
                
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_filename = temp_wav.name
                
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
                    
            # Send to transcription service
            with open(temp_filename, "rb") as audio_file:
                transcript = self.transcription_service.transcribe_with_openai(audio_file)
                
            # Add the transcribed text if any
            if transcript and self.text_callback:
                self.text_callback(transcript + " ")
                
            # Clean up temp file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
        except Exception as e:
            self.update_status(f"Error processing audio chunk: {str(e)}")
            
    def detect_audio_sources(self):
        """
        Detect available audio sources and return information.
        Useful for setup and troubleshooting.
        
        Returns:
            dict: Information about available audio devices
        """
        try:
            devices = sd.query_devices()
            input_devices = []
            output_devices = []
            loopback_devices = []
            
            # Categorize devices
            for i, device in enumerate(devices):
                device_info = {
                    'id': i,
                    'name': device['name'],
                    'channels': device.get('max_input_channels', 0),
                    'default': device.get('default_input', False)
                }
                
                # Check if it's an input device
                if device.get('max_input_channels', 0) > 0:
                    input_devices.append(device_info)
                    
                    # Check if it might be a loopback device
                    device_name = device['name'].lower()
                    if any(name in device_name for name in ['stereo mix', 'what u hear', 'loopback', 'monitor']):
                        loopback_devices.append(device_info)
                
                # Check if it's an output device
                if device.get('max_output_channels', 0) > 0:
                    output_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device.get('max_output_channels', 0),
                        'default': device.get('default_output', False)
                    })
                    
            return {
                'all_devices': devices,
                'input_devices': input_devices,
                'output_devices': output_devices,
                'loopback_devices': loopback_devices,
                'selected_device': self.audio_device_id,
                'selected_device_name': devices[self.audio_device_id]['name'] if self.audio_device_id is not None else None
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'selected_device': self.audio_device_id
            }
            
    def configure_device(self, device_id):
        """
        Configure which audio device to use for system audio capture.
        
        Args:
            device_id: ID of the audio device to use
            
        Returns:
            bool: True if device was set successfully
        """
        try:
            devices = sd.query_devices()
            if 0 <= device_id < len(devices):
                self.audio_device_id = device_id
                self.update_status(f"System audio device set to: {devices[device_id]['name']}")
                return True
            else:
                self.update_status(f"Invalid device ID: {device_id}")
                return False
        except Exception as e:
            self.update_status(f"Error configuring audio device: {str(e)}")
            return False
            
    def set_continuous_mode(self, enabled, chunk_duration=10):
        """
        Enable or disable continuous transcription mode.
        
        Args:
            enabled: True to enable continuous mode, False to disable
            chunk_duration: Duration in seconds of each audio chunk to process
            
        Returns:
            bool: True if mode was changed
        """
        self.continuous_mode = enabled
        self.chunk_duration = chunk_duration
        self.update_status(f"Continuous transcription mode {'enabled' if enabled else 'disabled'}")
        return True