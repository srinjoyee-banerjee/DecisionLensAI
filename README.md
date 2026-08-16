# DecisionLens AI

RAG + LLM + Agentic AI decision-support application.

## Features

- Semantic RAG retrieval
- Agent tool selection
- Decision scoring workflow
- Gemini LLM reasoning
- Evidence display
- Two-page web interface

## Stack

Python, Flask, Sentence Transformers, NumPy,
Google Gemini, HTML, CSS, JavaScript, Render.

## Render

Build Command:

pip install -r requirements.txt

Start Command:

gunicorn app:app

Environment Variable:

GEMINI_API_KEY

Optional:

GEMINI_MODEL=gemini-3.6-flash
