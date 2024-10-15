let mediaRecorder;
let audioChunks = [];
let selectedLanguage = '';
let screenStream; // Variável para armazenar o stream de compartilhamento de tela

// Função para iniciar a gravação de áudio
async function startRecording(language) {
    console.log("Idioma selecionado na gravação:", language);
    try {
        selectedLanguage = language;
        screenStream = await navigator.mediaDevices.getDisplayMedia({ audio: true, video: true });

        // Adiciona um listener para o evento de 'ended' do stream
        screenStream.getTracks()[0].addEventListener('ended', () => {
            chrome.runtime.sendMessage({ action: "screenSharingStopped" });
        });

        const microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Combina os streams de áudio
        const combinedStream = new MediaStream([...screenStream.getAudioTracks(), ...microphoneStream.getAudioTracks()]);

        mediaRecorder = new MediaRecorder(combinedStream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            const reader = new FileReader();

            reader.onloadend = function () {
                const base64AudioMessage = reader.result.split(',')[1];

                // Enviar áudio gravado para a API Flask
                fetch("http://localhost:5000/upload", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        audio: base64AudioMessage,
                        language: selectedLanguage,
                    }),
                })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Transcrição:", data.transcription);
                    console.log("Resumo:", data.summary);
                    openSummaryInSidebar(data.summary); // Abre a ata em uma janela lateral
                })
                .catch((error) => console.error("Erro ao enviar o áudio:", error));
            };

            reader.readAsDataURL(audioBlob);
        };

        mediaRecorder.start();
        console.log("Gravação iniciada...");
    } catch (error) {
        console.error("Erro ao capturar mídia:", error);
    }
}

// Função para parar a gravação
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        console.log("Gravação parada...");
    }
    stopScreenSharing(); // Chamada para parar o compartilhamento de tela
}

// Função para encerrar o compartilhamento de tela
function stopScreenSharing() {
    if (screenStream) {
        screenStream.getTracks().forEach(track => track.stop());
        console.log("Compartilhamento de tela encerrado.");
    }
}

// Função para abrir a ata em uma janela lateral
function openSummaryInSidebar(summary) {
    const sidebar = window.open("", "summarySidebar", "width=400,height=600");
    sidebar.document.write(`<html>
    <head>
        <title>Ata da Reunião</title>
        <style>
            body { 
                font-family: 'Arial', sans-serif; 
                margin: 20px; 
                background-color: #f4f4f4; 
                color: #333; 
                line-height: 1.6;
            }
            h2 { 
                color: #2c3e50; 
                border-bottom: 2px solid #3498db; 
                padding-bottom: 10px; 
                margin-bottom: 20px; 
            }
            p { 
                margin: 10px 0; 
                padding: 10px; 
                background: #fff; 
                border-left: 4px solid #3498db; 
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); 
            }
            .summary { 
                margin-top: 20px; 
                padding: 15px; 
                background-color: #ecf0f1; 
                border-radius: 5px; 
            }
            .footer { 
                margin-top: 30px; 
                font-size: 0.9em; 
                color: #7f8c8d; 
                text-align: center; 
            }
        </style>
    </head>
    <body>            
        <h2>Ata da Reunião</h2>
        <div class="summary">
            <p>${summary.replace(/\n/g, "<br>")}</p>
        </div>
        <div class="footer">
            <p>Esta ata foi gerada automaticamente.</p>
        </div>
    </body>
</html>`);
}

// Listener para receber mensagens do background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "startRecording") {
        startRecording(request.language);
        sendResponse({ status: "Recording started" });
    } else if (request.action === "stopRecording") {
        stopRecording();
        sendResponse({ status: "Recording stopped" });
    } else {
        console.error("Ação não reconhecida:", request.action);
        sendResponse({ status: "Ação não reconhecida" });
    }
});