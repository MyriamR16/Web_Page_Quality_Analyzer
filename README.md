# Web Page Quality Analyzer

Analyseur de qualité de pages web avec :
- une API Flask (`api/`)
- une interface React + Vite (`app/`)

## Prérequis

- Python 3.10+

## run the API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

API available on `http://127.0.0.1:5000`.

## run the front

```bash
cd app
npm install
npm run dev
```

Front available on `http://localhost:5173`.