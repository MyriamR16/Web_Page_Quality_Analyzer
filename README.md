# Web Page Quality Analyzer

## About

Web Page Quality Analyzer provides a comprehensive toolkit for assessing website quality through automated analysis, and generates comprehensive quality reports using LLMs.

## Architecture

The application consists of:
- a Flask API (`api/`)
- a React + Vite frontend (`app/`)

## Prerequisites

- Python 3.10+
- Node.js 18+
- Cohere API key (get one at https://cohere.com)

## Run the API

### 1. Configure environment variables

Create a `.env` file in the `api/` directory:

```bash
cd api
cp .env.example .env
```

Edit `.env` and add your Cohere API key:
```
COHERE_API_KEY=your_cohere_api_key_here
```

### 2. Install dependencies and run

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
python main.py
```

API available on `http://127.0.0.1:5000`.

## Run the frontend

```bash
cd app
npm install
npm run dev
```

Frontend available on `http://localhost:5173`.
