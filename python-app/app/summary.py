import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import tiktoken
from datetime import datetime

model = "gpt-4-32k"
token_limit = 32200

def limit_tokens(text, model, token_limit):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    token_chunks = [tokens[i:i + token_limit] for i in range(0, len(tokens), token_limit)]
    limited_texts = [encoding.decode(chunk) for chunk in token_chunks]
    return limited_texts

def generate_meeting_summary(transcription):
    limited_transcriptions = limit_tokens(transcription, model, token_limit)
    combined_notes = []

    if transcription == "" or len(transcription) < 100:
        return "Não foi possivel realizar a transcrição da reunião"
    
    for limited_transcription in limited_transcriptions:
        prompt = (f"A partir da seguinte transcrição de gravação:\n\n{limited_transcription}\n\n"
                "Faça um pequeno resumo.")        
        notes = generate_content(prompt)
        combined_notes.append(notes.content.strip())
    all_notes = "\n\n".join(combined_notes)
    
    
    final_prompt = (f"A partir das seguintes notas coletadas:\n\n{all_notes}\n\n"
                "Por favor, gere uma ata da reunião completa em português e inglês. "
                "Caso não consige formar uma Ata, faça um resumo sobre o tema abordado"
                "Formate o texto em HTML com adequados. "
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