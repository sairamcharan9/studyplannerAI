# StudyplannerAI

An AI-powered study plan generator that creates personalized learning roadmaps based on research and user requirements.

## Features

- **Research-Based Plans**: Utilizes web search to gather the latest information on your chosen topic
- **AI-Generated Roadmaps**: Creates structured, step-by-step learning plans using Ollama LLM
- **Customizable Options**: Adjust duration, detail level, learning style, and prior knowledge
- **Resource Recommendations**: Suggests books, courses, videos, and other learning materials
- **Modern Web Interface**: Clean, responsive UI built with FastAPI and Tailwind CSS
- **Facial Expression Analysis**: (New!) Analyzes student facial expressions during study sessions to provide insights into engagement and focus.

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- [Ollama](https://ollama.ai) installed and running locally (default: http://localhost:11434)
- `opencv-python` and `numpy` for facial analysis (installed via `requirements.txt`)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/StudyplannerAI.git
   cd StudyplannerAI
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your configuration:
   ```
   # .env
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

### Facial Expression Analysis Setup

To enable the facial expression analysis feature:

1.  **Enable in Settings:** Navigate to the `/settings` page in the application and toggle "Enable Facial Expression Analysis" to `true`.
2.  **Environment Variable:** Ensure the following is set in your `.env` file:
    ```
    ENABLE_FACIAL_ANALYSIS=true
    ```
3.  **Privacy Policy:** Review the [Privacy Policy](PRIVACY_POLICY.md) regarding facial data collection and usage. Explicit user consent is required before camera access is initiated.

### Running the Application

1. Start the application:
   ```
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Architecture

The application uses a modular architecture:

- **FastAPI Backend**: RESTful API endpoints for generating study plans, including facial analysis.
- **Research Service**: Scrapes and analyzes web content to gather relevant information
- **Ollama Service**: Communicates with the Ollama API to generate structured study plans
- **OpenRouter Service**: Communicates with the OpenRouter API to generate structured study plans
- **Gemini Service**: Communicates with the Google Gemini API to generate structured study plans
- **Facial Analysis Data Service**: (New!) Handles storage of facial expression analysis logs.
- **Study Plan Service**: Coordinates between research and AI generation
- **Jinja2 Templates**: Server-side rendering for the web interface
- **Tailwind CSS**: Utility-first CSS framework for styling

## API Integration

The application supports multiple AI providers. You can choose which provider to use by setting the `AI_PROVIDER` environment variable.

- `ollama`: (Default) Uses a local Ollama instance.
- `openrouter`: Uses the OpenRouter API. Requires an `OPENROUTER_API_KEY`.
- `gemini`: Uses the Google Gemini API. Requires a `GEMINI_API_KEY`.

### Ollama

To use Ollama, set the following environment variables:

```
# .env
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

### OpenRouter

To use OpenRouter, set the following environment variables:

```
# .env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

### Google Gemini

To use Google Gemini, set the following environment variables:

```
# .env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

## Customizing the Application

### Changing the AI Model

You can switch to a different Ollama model by modifying the `.env` file or changing the `OLLAMA_MODEL` environment variable.

### Modifying the Web Interface

The web interface uses Jinja2 templates located in the `templates` directory and JavaScript in the `static/js` directory.

## Contributing

We welcome contributions to StudyplannerAI! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to get started, report issues, and submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
