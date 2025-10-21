# StudyplannerAI

An AI-powered study plan generator that creates personalized learning roadmaps based on research and user requirements.

## Features

- **Research-Based Plans**: Utilizes web search to gather the latest information on your chosen topic
- **AI-Generated Roadmaps**: Creates structured, step-by-step learning plans using Gemini LLM
- **Customizable Options**: Adjust duration, detail level, learning style, and prior knowledge
- **Resource Recommendations**: Suggests books, courses, videos, and other learning materials
- **Modern Web Interface**: Clean, responsive UI built with FastAPI and Tailwind CSS

## Setup Instructions

### Prerequisites

- Python 3.8+ installed

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
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=google/gemini-2.0-flash-exp:free
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
- **Gemini Service**: Communicates with the Gemini API to generate structured study plans
- **Study Plan Service**: Coordinates between research and AI generation
- **Jinja2 Templates**: Server-side rendering for the web interface
- **Tailwind CSS**: Utility-first CSS framework for styling

## API Integration

The application currently uses Gemini for AI model integration. Future versions plan to include:

1. Enhanced web research capabilities
2. PDF export functionality
3. User accounts and saved study plans

## Customizing the Application

### Changing the AI Model

You can switch to a different Gemini model by modifying the `.env` file or changing the `GEMINI_MODEL` environment variable.

### Modifying the Web Interface

The web interface uses Jinja2 templates located in the `templates` directory and JavaScript in the `static/js` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
