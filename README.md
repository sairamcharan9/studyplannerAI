# StudyplannerAI

An AI-powered study plan generator that creates personalized learning roadmaps based on research and user requirements.

## Features

- **Research-Based Plans**: Utilizes web search to gather the latest information on your chosen topic
- **AI-Generated Roadmaps**: Creates structured, step-by-step learning plans using Ollama LLM
- **Customizable Options**: Adjust duration, detail level, learning style, and prior knowledge
- **Resource Recommendations**: Suggests books, courses, videos, and other learning materials
- **Modern Web Interface**: Clean, responsive UI built with FastAPI and Tailwind CSS

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- [Ollama](https://ollama.ai) installed and running locally (default: http://localhost:11434)

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
     venv\Scripts\activate
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

- **FastAPI Backend**: RESTful API endpoints for generating study plans
- **Research Service**: Scrapes and analyzes web content to gather relevant information
- **Ollama Service**: Communicates with the Ollama API to generate structured study plans
- **Study Plan Service**: Coordinates between research and AI generation
- **Jinja2 Templates**: Server-side rendering for the web interface
- **Tailwind CSS**: Utility-first CSS framework for styling

## API Integration

The application currently uses Ollama for local AI model integration. Future versions plan to include:

1. Integration with additional AI APIs (OpenAI, Google Gemini, etc.)
2. Enhanced web research capabilities
3. PDF export functionality
4. User accounts and saved study plans

## Customizing the Application

### Changing the AI Model

You can switch to a different Ollama model by modifying the `.env` file or changing the `OLLAMA_MODEL` environment variable.

### Modifying the Web Interface

The web interface uses Jinja2 templates located in the `templates` directory and JavaScript in the `static/js` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
