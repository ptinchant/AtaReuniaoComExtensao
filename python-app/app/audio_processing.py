import base64
import subprocess
import magic
from pydub import AudioSegment

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