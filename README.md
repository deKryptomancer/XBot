# Ollama Chat Agent

A simple GUI chat interface for interacting with Ollama language models.

## Features

- Clean, modern GUI built with Tkinter
- Dynamically loads available Ollama models
- Simple and intuitive chat interface
- Multi-line input support
- Error handling and connection status

## Prerequisites

- Python 3.7 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- At least one Ollama model downloaded (e.g., `ollama pull llama3`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd XBot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure Ollama is running locally
2. Run the application:
   ```bash
   python ollama_chat_agent.py
   ```
3. Select a model from the dropdown menu
4. Type your message and press Enter to send

## Project Structure

- `ollama_chat_agent.py` - Main application file
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore file

## License

This project is open source and available under the [MIT License](LICENSE).
