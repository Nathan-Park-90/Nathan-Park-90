from flask import Flask, request, jsonify
import os
import tempfile
from pyannote.audio import Pipeline # Added import for Pipeline
import torch
import torchaudio
# import whisper # Placeholder for actual whisper import

app = Flask(__name__)

# Whisper Model Placeholder
whisper_model = None
# Pyannote Pipeline Placeholder
diarization_pipeline = None

def load_whisper_model():
    """
    Placeholder function for loading the Whisper model.
    """
    print("INFO: Whisper model is currently a placeholder (`whisper_model = None`). Actual model loading (e.g., `whisper.load_model('base.en')`) needs to be implemented if a real model is required.")
    # Actual model loading logic will be implemented here later.

def load_diarization_pipeline():
    """
    Placeholder function for loading the Pyannote diarization pipeline.
    """
    global diarization_pipeline
    HF_TOKEN = os.environ.get("HF_TOKEN")
    print("INFO: Attempting to load pyannote.audio pipeline...")
    try:
        if HF_TOKEN:
            print("INFO: Using HF_TOKEN for pyannote.audio pipeline.")
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=HF_TOKEN 
            )
        else:
            print("INFO: HF_TOKEN not found. Attempting to load pyannote/speaker-diarization-3.1 without explicit token (might use cached model or fail if auth is strictly required).")
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1"
            )
        diarization_pipeline = pipeline
        print("INFO: pyannote.audio speaker diarization pipeline loaded successfully.")
    except Exception as e:
        print(f"ERROR: Failed to load pyannote.audio pipeline: {e}")
        diarization_pipeline = None # Ensure it's None if loading fails

# Call load_whisper_model and load_diarization_pipeline when the script starts
load_whisper_model()
load_diarization_pipeline()

@app.route('/', methods=['GET'])
def hello_world():
    """
    Root route to check if the Flask app is running.
    """
    return "Flask App is Running!"

@app.route('/process_audio_diarized', methods=['POST'])
def process_audio_diarized():
    """
    Processes audio file, performs diarization (placeholder).
    """
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file part"}), 400
    
    file = request.files['audio_file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        file.save(temp_audio_file.name)
        temp_file_path = temp_audio_file.name # Store path for response
        print(f"INFO: Audio file saved to temporary path: {temp_file_path}")

        if diarization_pipeline is None:
            temp_audio_file.close()
            os.unlink(temp_file_path)
            return jsonify({"error": "Diarization pipeline not available"}), 500

        print(f"INFO: Applying diarization to {temp_file_path}")
        try:
            diarization_result = diarization_pipeline(temp_file_path) # temp_audio_file.name is temp_file_path
            
            transcribed_segments = []
            try:
                waveform, sample_rate = torchaudio.load(temp_file_path)
            except Exception as e:
                temp_audio_file.close()
                os.unlink(temp_file_path)
                return jsonify({"error": f"Failed to load audio for segmentation: {e}"}), 500

            for segment, track_name, speaker_label in diarization_result.itertracks(yield_label=True):
                start_time = segment.start
                end_time = segment.end
                
                start_frame = int(start_time * sample_rate)
                end_frame = int(end_time * sample_rate)
                segment_waveform = waveform[:, start_frame:end_frame]
                
                segment_audio_path = "" # Initialize
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_segment_file:
                    torchaudio.save(tmp_segment_file.name, segment_waveform, sample_rate)
                    segment_audio_path = tmp_segment_file.name
                
                # Simulate Transcription
                transcription_text = f"Simulated transcription for {speaker_label} from {start_time:.2f}s to {end_time:.2f}s."
                print(f"DEBUG: Simulating transcription for segment: {segment_audio_path}")
                
                transcribed_segments.append({
                    "speaker": speaker_label,
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": transcription_text,
                    "segment_temp_file": segment_audio_path 
                })
                
                os.unlink(segment_audio_path) # Clean up temporary segment file
            
            final_transcript = []
            for seg in transcribed_segments:
                final_transcript.append({
                    "speaker": seg["speaker"],
                    "start_time": round(seg["start_time"], 3), # Round to 3 decimal places
                    "end_time": round(seg["end_time"], 3),   # Round to 3 decimal places
                    "text": seg["text"]
                })

            return jsonify({"transcript": final_transcript})

        except Exception as e: # This is the main general exception handler
            print(f"ERROR: An unexpected error occurred: {e}")
            # The finally block below will handle cleanup of temp_audio_file
            return jsonify({"error": "An unexpected error occurred during processing."}), 500
        finally:
            # Cleanup for the original temporary audio file
            if 'temp_audio_file' in locals() and hasattr(temp_audio_file, 'name') and os.path.exists(temp_audio_file.name):
                try:
                    temp_audio_file.close() # Close the file handle
                    os.unlink(temp_audio_file.name) # Delete the file
                    print(f"INFO: Original temporary audio file {temp_audio_file.name} deleted.")
                except Exception as e:
                    print(f"ERROR: Could not delete temporary file {temp_audio_file.name}: {e}")

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
