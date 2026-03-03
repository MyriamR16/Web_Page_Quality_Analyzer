# Web Page Quality Analyzer

## About

Web Page Quality Analyzer provides a comprehensive toolkit for assessing website quality through automated analysis, and generates comprehensive quality reports.

## Architecture

The application consists of:
- a Flask API (`api/`)
- a React + Vite frontend (`app/`)

## Prerequisites

- Python 3.10+

## Run the API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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