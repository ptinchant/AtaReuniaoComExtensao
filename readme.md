# FLOW! Meeting Transcriber

Um aplicativo para transcrever reuniões e gerar resumos automaticamente.

## Descrição

O FLOW! Meeting Transcriber é uma extensão para o Chrome que permite gravar áudio de reuniões, transcrever o conteúdo e gerar um resumo da reunião. A extensão suporta múltiplos idiomas e é fácil de usar.

## Funcionalidades

- **Gravação de Áudio**: Inicie e pare a gravação de reuniões diretamente do navegador.
- **Transcrição Automática**: O áudio gravado é transcrito em texto em tempo real.
- **Suporte a Múltiplos Idiomas**: Escolha o idioma da transcrição (por exemplo, Português, Inglês, etc.).
- **Geração de Resumos**: Após a transcrição, um resumo da reunião é gerado e exibido de forma organizada.
- **Interface Simples**: A extensão possui uma interface amigável para fácil navegação.

## Tecnologias Usadas

- **JavaScript**: Para a lógica da extensão.
- **HTML/CSS**: Para a interface do usuário.
- **Whisper API**: Para transcrição de áudio.
- **Python**: Para o backend e manipulação de transcrição.

## Instalação

### 1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/flow-meeting-transcriber.git
```

### 2. Acesse a pasta do projeto:

```bash
cd flow-meeting-transcriber
```

### 3. Instale as dependências do Python:

Certifique-se de ter o Python instalado. Depois, instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

### 4. Execute o aplicativo Python:

Inicie o servidor Flask (ou qualquer outro backend que você esteja usando):

```bash
python app.py
```

### 5. Abra o Chrome e acesse `chrome://extensions/`.

- Ative o "Modo do desenvolvedor" no canto superior direito.
- Clique em "Carregar sem compactação" e selecione a pasta do projeto.

## Uso

1. Clique com o botão direito do mouse na página e selecione "Meeting Transcriber".
2. Escolha a opção "Start Recording" para iniciar a gravação.
3. Após a reunião, selecione "Stop Recording" e escolha o idioma.
4. A ata da reunião será gerada e exibida em uma nova janela.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

## Contato

- **Pierre Tinchant Pinto**: [pierre.pinto@ciandt.com](mailto:pierre.pinto@ciandt.com)
- **GitHub**: [ptinchant](https://github.com/ptinchant)

