import whisper

# Load the model (defaults to "base" which is smaller and faster)
model = whisper.load_model("medium")

# Transcribe the audio file
result = model.transcribe("recording.mp3")

# Open file to write results
with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write("Full Transcription:\n")
    f.write(result["text"])
    f.write("\n\nSegments in 30-second intervals:\n")
    
    current_segment = ""
    current_start = 0

    for segment in result["segments"]:
        if segment['start'] - current_start >= 30:
            if current_segment:
                f.write(f"[{current_start:.2f}s -> {segment['start']:.2f}s] {current_segment}\n")
            current_segment = segment['text']
            current_start = segment['start']
        else:
            current_segment += " " + segment['text']

    if current_segment:
        f.write(f"[{current_start:.2f}s -> {segment['end']:.2f}s] {current_segment}\n")
