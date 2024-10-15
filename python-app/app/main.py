from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from audio_processing import extract_audio_from_webm, identify_file_type
from transcription import process_audio
from summary import generate_meeting_summary
from environment import setup_environment
import base64

app = FastAPI()

# Configurando CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_audio(data: dict):
    print("Dados recebidos")
    
    file_type = identify_file_type(data["audio"])
    audio_data = base64.b64decode(data["audio"])
    
    if file_type == "video/webm":
        output_audio_file = "audio.wav"
        extract_error = extract_audio_from_webm(audio_data, output_audio_file)
        if extract_error:
            raise HTTPException(status_code=400, detail=extract_error)
    else:
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado.")

    
    full_transcription = process_audio(output_audio_file, data.get("language", "auto"))
    summary = generate_meeting_summary(full_transcription)

    return JSONResponse(content={"transcription": full_transcription, "summary": summary})

if __name__ == "__main__":
    setup_environment()
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)