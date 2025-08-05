# Advanced RAG Q&A Application

This project is a full-stack Question-Answering application that leverages a sophisticated Retrieval-Augmented Generation (RAG) pipeline to answer user queries. It uses real-time web retrieval to gather context and provides accurate, flexible, and well-grounded answers through an interactive chat interface.

This system is designed to be robust, handling cases where context is incomplete or irrelevant by intelligently blending retrieved information with the language model's general knowledge.

---

## Key Features

- **Real-time Web Retrieval:** Utilizes the Tavily API to fetch up-to-date information from the web to serve as context for the LLM.
- **Flexible RAG Pipeline:** Implements an advanced RAG chain that prioritizes provided context but can gracefully fall back on general knowledge, ensuring a helpful response in all scenarios.
- **Intelligent Document Processing:** Includes a custom pre-processing step to clean and format noisy web documents before they are passed to the language model, significantly improving response accuracy.
- **Transparent Sourcing:** The model is instructed to be transparent about its information sources, indicating whether an answer comes from the provided documents or its general knowledge.
- **Full-Stack Architecture:** Features a modern React frontend with Tailwind CSS and a robust Python backend built with LangChain, ready for deployment.

---

## Tech Stack

### Backend
- **Python 3.10+**
- **LangChain & LCEL (LangChain Expression Language):** For building and composing the RAG pipeline.
- **OpenAI GPT-4o:** As the core language model for generation.
- **Tavily AI:** For real-time web search and document retrieval.
- **FastAPI (or Flask):** For serving the REST API.
- **Render:** For cloud deployment and hosting.

### Frontend
- **React.js:** For building the user interface.
- **Vite:** As the frontend build tool.
- **Tailwind CSS:** For styling the user interface.

---

## System Architecture & How It Works

The application follows a carefully orchestrated RAG pipeline to ensure high-quality responses.
- [User Query] -> [React Frontend] -> [Backend API] -> [RAG Chain] -> [LLM] -> [Formatted Answer]

---

## Getting Started

Follow these instructions to get a local copy of the project up and running.

### Prerequisites

- Python 3.10+ and Pip
- Node.js and npm
- Git

### Backend Setup

1.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory and add your API keys:
    ```
    OPENAI_API_KEY="sk-..."
    TAVILY_API_KEY="tvly-..."
    ```

2.  **Run the backend server:**
    ```sh
    # Assuming you are using FastAPI with a file named main.py
    uvicorn main:app --reload
    ```
    The backend will be running on `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Set up environment variables:**
    Create a `.env.local` file in the `frontend` directory and specify the backend API URL:
    ```
    VITE_API_URL="http://127.0.0.1:8000"
    ```

2.  **Run the frontend development server:**
    ```sh
    npm run dev
    ```
    Open `http://localhost:5173` (or the URL provided) in your browser.

---
