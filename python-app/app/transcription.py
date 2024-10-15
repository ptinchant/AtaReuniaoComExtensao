import speech_recognition as sr
from pydub import AudioSegment
from fastapi import HTTPException

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
            return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f""

def process_audio(audio_file, language):
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_wav(audio_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o áudio: {e}")

    chunk_length = 30000  # tamanho do chunk (max 30s)
    full_transcription = ""

    chunks = [audio[i:i + chunk_length] for i in range(0, len(audio), chunk_length)]

    for chunk in chunks:
        chunk.export("chunk.wav", format="wav")
        try:
            with sr.AudioFile("chunk.wav") as source:
                audio = recognizer.record(source)
                text = get_best_transcription(recognizer, audio, language)
                full_transcription += text + " "
        except Exception as e:
            full_transcription += f"[Erro ao processar o chunk: {e}]"

    return full_transcription