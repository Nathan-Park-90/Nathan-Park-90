# Speaker Diarization and Transcription Flask App

This Flask application provides an API endpoint to process an audio file, perform speaker diarization, and return a labeled transcript.

## Features

-   Accepts audio file uploads (WAV, MP3 should be supported by common libraries like FFMPEG which is a dependency).
-   Performs speaker diarization using `pyannote.audio` (`pyannote/speaker-diarization-3.1` model).
-   Transcribes audio segments per speaker (currently simulated, uses placeholder text).
-   Returns a structured JSON response with speaker labels, start/end times, and transcribed text.

## Setup and Running

### Prerequisites

-   Docker
-   Hugging Face Hub Token (optional, but recommended for `pyannote.audio` models)

### Environment Variables

-   `HF_TOKEN`: (Optional) Your Hugging Face Hub token. If the `pyannote/speaker-diarization-3.1` model requires authentication and you don't provide a token, diarization may fail.
-   `PORT`: (Optional) The port on which the Flask application will run. Defaults to `8080`.

### Building and Running with Docker

1.  **Clone the repository** (or ensure all files: `app.py`, `requirements.txt`, `Dockerfile` are in the same directory).
2.  **Build the Docker image**:
    ```bash
    docker build -t diarization-app .
    ```
3.  **Run the Docker container**:
    ```bash
    docker run -p 8080:8080 -e HF_TOKEN="YOUR_HF_TOKEN_HERE" diarization-app
    ```
    Replace `YOUR_HF_TOKEN_HERE` with your actual Hugging Face token if you have one. The `-e HF_TOKEN` part is optional if the model can be downloaded without it. The port mapping `-p 8080:8080` assumes the app runs on port 8080 inside the container (which it does by default).

## API Endpoint

### `/process_audio_diarized`

-   **Method**: `POST`
-   **Description**: Upload an audio file for diarization and (simulated) transcription.
-   **Form Data**:
    -   `audio_file`: The audio file to process.
-   **Success Response (200 OK)**:
    ```json
    {
      "transcript": [
        {
          "speaker": "SPEAKER_00",
          "start_time": 0.532,
          "end_time": 2.332,
          "text": "Simulated transcription for SPEAKER_00 from 0.53s to 2.33s."
        },
        {
          "speaker": "SPEAKER_01",
          "start_time": 2.851,
          "end_time": 4.512,
          "text": "Simulated transcription for SPEAKER_01 from 2.85s to 4.51s."
        }
      ]
    }
    ```
-   **Error Responses**:
    -   `400 Bad Request`: If `audio_file` part is missing or no file is selected.
        ```json
        {"error": "No audio file part"}
        ```
        ```json
        {"error": "No selected file"}
        ```
    -   `500 Internal Server Error`: If the diarization pipeline is not available or an unexpected error occurs during processing.
        ```json
        {"error": "Diarization pipeline not available"}
        ```
        ```json
        {"error": "An unexpected error occurred during processing."}
        ```
        ```json
        {"error": "Failed to load audio for segmentation: [specific error]"}
        ```

## Notes

-   **Whisper Transcription**: The actual speech-to-text transcription using `openai-whisper` is currently **simulated**. The `whisper_model` is set to `None` in `app.py`, and placeholder text is generated. To implement actual transcription, the `whisper_model` would need to be loaded (e.g., `whisper.load_model("base.en")`) and the simulated transcription logic in `process_audio_diarized` replaced with calls to `whisper_model.transcribe()`.
-   **Audio Formats**: While `ffmpeg` is installed (a common dependency for `torchaudio` and `pyannote.audio`), ensure your uploaded audio files are in a format readily processable by these libraries (e.g., WAV, MP3). The temporary file created for processing is a `.wav` file.
