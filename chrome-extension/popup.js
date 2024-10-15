document.getElementById('startBtn').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: "startRecording" });
  });
  
  document.getElementById('stopBtn').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: "stopRecording" });
  });
  
  chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "updateButtons") {
      document.getElementById('startBtn').disabled = request.isRecording;
      document.getElementById('stopBtn').disabled = !request.isRecording;
      document.getElementById('language').innerText = request.language;
    }
  });
  