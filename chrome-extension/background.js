let selectedLanguage = "none"; // Idioma padrão: nenhum selecionado

console.log("Content script carregado.");

// Função para iniciar a gravação de áudio
function startRecording(tabId) {
    console.log("Tab ID para iniciar gravação:", tabId);
    chrome.tabs.sendMessage(tabId, { action: "startRecording", language: selectedLanguage }, (response) => {
        if (chrome.runtime.lastError) {
            console.error("Erro ao enviar mensagem para contentScript:", chrome.runtime.lastError.message);
        } else {
            console.log("Resposta do contentScript:", response);
        }
    });
}

// Função para parar a gravação
function stopRecording(tabId) {
    console.log("Tab ID para parar gravação:", tabId);
    
    if (selectedLanguage === "auto") {
        // Se o idioma não foi selecionado, notifique o usuário
        chrome.notifications.create({
            type: "basic",
            iconUrl: "icon.png", // Substitua pelo caminho do seu ícone
            title: "Atenção",
            message: "Por favor, selecione um idioma antes de parar a gravação." + selectedLanguage,
            priority: 2
        });
        chrome.contextMenus.update("startRecording", { enabled: false });
        chrome.contextMenus.update("stopRecording", { enabled: true });
        return; // Não para a gravação se o idioma não estiver selecionado
    }

    chrome.tabs.sendMessage(tabId, { action: "stopRecording", language: selectedLanguage });
}

// Listener para ações nos menus de contexto
chrome.contextMenus.onClicked.addListener((info, tab) => {
    debugger;
    if (info.menuItemId === "startRecording") {
        startRecording(tab.id);
        chrome.contextMenus.update("startRecording", { enabled: false });
        chrome.contextMenus.update("stopRecording", { enabled: true });
    } else if (info.menuItemId === "stopRecording") {
        stopRecording(tab.id);
        chrome.contextMenus.update("startRecording", { enabled: true });
        chrome.contextMenus.update("stopRecording", { enabled: false });
    } else if (info.menuItemId.startsWith("setLanguage_")) {
        selectedLanguage = info.menuItemId.split("_")[1]; // Atualiza o idioma selecionado
        console.log("Idioma selecionado:", selectedLanguage);
        
        // Habilita a opção de parar a gravação se um idioma válido for selecionado
        chrome.contextMenus.update("stopRecording", { enabled: selectedLanguage !== "auto" });
    }
});

// Criar os menus de contexto quando a extensão é instalada
chrome.runtime.onInstalled.addListener(() => {
    // Menu principal
    chrome.contextMenus.create({
        id: "recordingMenu",
        title: "Meeting Transcriber",
        contexts: ["all"],
    });

    // Opção de iniciar gravação
    chrome.contextMenus.create({
        id: "startRecording",
        parentId: "recordingMenu",
        title: "Start Recording",
        contexts: ["all"],
        enabled: true,
    });

    // Opção de parar gravação
    chrome.contextMenus.create({
        id: "stopRecording",
        parentId: "recordingMenu",
        title: "Stop Recording",
        contexts: ["all"],
        enabled: false,
    });

    // Criar submenu para idiomas
    const languageMenuId = "languageMenu";
    chrome.contextMenus.create({
        id: languageMenuId,
        parentId: "recordingMenu",
        title: "Selecionar Idioma",
        contexts: ["all"],
    });

    // Adicionar opções de idioma como submenus
    chrome.contextMenus.create({
        id: "setLanguage_auto",
        parentId: languageMenuId,
        title: "Nenhum idioma",
        contexts: ["all"],
    });

    chrome.contextMenus.create({
        id: "setLanguage_pt",
        parentId: languageMenuId,
        title: "Português",
        contexts: ["all"],
    });

    chrome.contextMenus.create({
        id: "setLanguage_en",
        parentId: languageMenuId,
        title: "Inglês",
        contexts: ["all"],
    });

    chrome.contextMenus.create({
      id: "setLanguage_none",
      parentId: languageMenuId,
      title: "Identificar automaticamente(Impreciso)",
      contexts: ["all"],
  });
});