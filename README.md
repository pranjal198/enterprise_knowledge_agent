# Enterprise Knowledge Assistant

A full-stack AI application that enables users to interact with PDF documents using **Retrieval-Augmented Generation (RAG)** and an **agentic tool-calling architecture**.

Built with React, FastAPI, Google Gemini, LangChain, and ChromaDB.

## Features

- **PDF Question Answering:** Upload documents and ask questions using RAG.
- **Semantic Search:** Retrieve relevant document chunks using vector embeddings.
- **AI Agent:** Dynamically selects and executes tools based on user queries.
- **Calculator Tool:** Performs mathematical calculations.
- **Web Search Tool:** Retrieves external information using Tavily.
- **Document Search Tool:** Answers questions using uploaded documents.

## Tech Stack

- **Frontend:** React, JavaScript, Vite
- **Backend:** Python, FastAPI
- **LLM:** Google Gemini
- **AI Framework:** LangChain
- **Vector Database:** ChromaDB
- **Embeddings:** Gemini Embedding
- **Web Search:** Tavily

## Project Structure

```text
enterprise-knowledge-assistant/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── core/
│   │   ├── generation/
│   │   ├── ingestion/
│   │   └── retrieval/
│   └── requirements.txt
├── data/
│   └── documents/
├── frontend/
│   └── src/
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pranjal198/enterprise_knowledge_agent.git
cd enterprise-knowledge-assistant
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 3. Install and run the backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 4. Run the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

## Running Tests

From the `backend` directory:

```powershell
..\.venv\Scripts\python.exe -m pytest
```

## Future Improvements

- Conversation memory and chat history
- Hybrid search and reranking
- User authentication
- Streaming responses
- Docker-based deployment

---

**Built to explore practical RAG systems, LLM tool calling, and AI agent orchestration.**
