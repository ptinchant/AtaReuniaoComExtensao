from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
import os
import subprocess
from pydub import AudioSegment
import speech_recognition as sr
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import jwt
import tiktoken
from datetime import datetime
import magic
import noisereduce as nr
import numpy as np

app = FastAPI()

# Configurando CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = "gpt-4-32k"
token_limit = 32200

def identify_file_type(base64_string):
    audio_data = base64.b64decode(base64_string)
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(audio_data)
    return file_type

def extract_audio_from_webm(webm_data, output_audio_path):
    webm_path = 'temp_video.webm'
    with open(webm_path, 'wb') as f:
        f.write(webm_data)

    command = [
        'ffmpeg',
        '-y',
        '-i', webm_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '48000',
        '-ac', '2',
        output_audio_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f'Áudio extraído com sucesso para: {output_audio_path}')
    except subprocess.CalledProcessError as e:
        print(f'Erro ao extrair áudio: {e}')
        return {"error": "Erro ao extrair áudio."}

def reduce_noise(audio_segment):
    samples = np.array(audio_segment.get_array_of_samples())
    reduced_noise = nr.reduce_noise(y=samples, sr=audio_segment.frame_rate)
    return AudioSegment(
        reduced_noise.tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width,
        channels=audio_segment.channels
    )

def get_best_transcription(recognizer, audio, language):
    try:
        results = recognizer.recognize_google(audio, language=language, show_all=True)
        
        if results:
            best_transcription = ""
            best_confidence = 0
            
            for result in results['alternative']:
                if 'confidence' in result:
                    confidence = result['confidence']
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_transcription = result['transcript']
                else:
                    best_transcription = result['transcript']
            
            return best_transcription
        else:
            return "[Inaudível]"
    except sr.UnknownValueError:
        return "[Inaudível]"
    except sr.RequestError as e:
        return f"[Erro: {e}]"

@app.post("/upload")
async def upload_audio(data: dict):
    print("Dados recebidos")
    
    chunk_length = 30000  # tamanho do chunk (max 30s)
    full_transcription = ""

    file_type = identify_file_type(data["audio"])
    
    audio_data = base64.b64decode(data["audio"])
    print("Tamanho do áudio recebido:", len(audio_data))
    selected_language = data.get("language", "auto")

    if file_type == "video/webm":
        output_audio_file = "audio.wav"
        extract_error = extract_audio_from_webm(audio_data, output_audio_file)
        if extract_error:
            raise HTTPException(status_code=400, detail=extract_error)
    else:
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado.")
    
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_wav("audio.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o áudio: {e}")
   
    chunks = [audio[i:i + chunk_length] for i in range(0, len(audio), chunk_length)]

    for i, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        try:
            with sr.AudioFile("chunk.wav") as source:
                audio = recognizer.record(source)
                text = get_best_transcription(recognizer, audio, selected_language)
                full_transcription += text + " "
        except Exception as e:
            full_transcription += f"[Erro ao processar o chunk: {e}]"

    summary = generate_meeting_summary(full_transcription)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    summary_filename = f"Summaries/{formatted_time}.txt"
    save_summary_to_txt(summary, summary_filename)

    return JSONResponse(content={"transcription": full_transcription, "summary": summary, "summaryFile": summary_filename})

def limit_tokens(text, model, token_limit):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    token_chunks = [tokens[i:i + token_limit] for i in range(0, len(tokens), token_limit)]
    limited_texts = [encoding.decode(chunk) for chunk in token_chunks]
    return limited_texts

def generate_meeting_summary(transcription):
    limited_transcriptions = limit_tokens(transcription, model, token_limit)
    combined_notes = []

    for limited_transcription in limited_transcriptions:
        prompt = (f"A partir da seguinte transcrição de gravação:\n\n{limited_transcription}\n\n"
                  "Faça um pequeno resumo sobre a gravação.")
        notes = generate_content(prompt)
        combined_notes.append(notes.content.strip())

    all_notes = "\n\n".join(combined_notes)
    final_prompt = (f"A partir das seguintes notas coletadas:\n\n{all_notes}\n\n"
                "Por favor, gere uma ata da reunião completa em português e inglês. "
                "Caso não consige formar uma Ata, faça um resumo sobre o tema abordado"
                "Formate o texto em HTML com estilos bonitos e adequados. "
                "Identifique o tema, informações importantes e, se possível, mencione as pessoas envolvidas. "
                "A ata deve incluir um título, listagens para tópicos discutidos e tarefas atribuídas. "
                "Use estilos como negrito e itálico onde apropriado. "
                "Não inclua a informação ```html.")
    final_summary = generate_content(final_prompt)
    return final_summary.content.strip()

def generate_content(prompt):
    flow_llm_url = os.environ.get("FLOW_LLM_ORCH_URL", "https://flow.ciandt.com/ai-orchestration-api/v1/openai")
    flow_tenant = os.environ.get("FLOW_TENANT")
    flow_token = os.getenv("FLOW_TOKEN")

    chat = ChatOpenAI(
        model_name="gpt-4-32k",
        openai_api_base=flow_llm_url,
        openai_api_key="please-ignore",
        default_headers={
            "FlowTenant": flow_tenant,
            "FlowAgent": "simple_agent",
            "Authorization": f"Bearer {flow_token}",
        },
    )

    messages = [HumanMessage(content=prompt)]
    return chat.invoke(messages)

def save_summary_to_txt(summary, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Ata e tarefas salvas em {filename}")

def setup_environment():
    summaries_folder = 'Summaries'
    if not os.path.exists(summaries_folder):
        os.makedirs(summaries_folder)

    load_dotenv()
    valid_token = False
    flowToken = os.environ.get("FLOW_TOKEN")
    if flowToken:
        decoded = jwt.decode(flowToken, options={"verify_signature": False})
        if datetime.fromtimestamp(decoded["exp"]) > datetime.now():
            valid_token = True

    if not valid_token:
        cmd = ["python", "python-app/flow_token.py"]
        subprocess.Popen(cmd).wait()

if __name__ == "__main__":
    setup_environment()
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)