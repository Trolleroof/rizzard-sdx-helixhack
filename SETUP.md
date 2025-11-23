# Rizzard Setup Guide

This guide will help you set up both the frontend and backend to work together.

## Backend Setup (FastAPI)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file in the `backend` directory:**
   ```bash
   CLAUDE_API=your-claude-api-key-here
   DEBUG=False
   APP_NAME=Rizzard AI Microservice
   ```

5. **Run the backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The backend will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`

## Frontend Setup (Next.js)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies (if not already done):**
   ```bash
   npm install
   ```

3. **Create `.env.local` file in the `frontend` directory:**
   ```bash
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

4. **Run the frontend:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## How It Works

1. **Frontend** (Next.js) runs on port 3000
2. **Backend** (FastAPI) runs on port 8000
3. The frontend Chat component calls the backend `/chat/` endpoint
4. The backend uses the Anthropic Python SDK to communicate with Claude
5. Responses are streamed back to the frontend in real-time

## API Key Setup

- **Backend**: Set `CLAUDE_API` in `backend/.env`
- The backend reads this key and uses it with the Anthropic Python SDK
- The API key never leaves the backend (secure!)

## Testing the Connection

1. Start the backend: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Start the frontend: `cd frontend && npm run dev`
3. Open `http://localhost:3000` in your browser
4. Try sending a message in the chat - it should connect to Claude via the backend!

## Troubleshooting

- **CORS errors**: Make sure the backend is running and CORS is configured (already done in `main.py`)
- **API key errors**: Check that `CLAUDE_API` is set in `backend/.env`
- **Connection refused**: Ensure backend is running on port 8000
- **Module not found**: Run `pip install -r requirements.txt` in the backend directory

