# Hi Rainbow AI App

A small Python + FastAPI project that provides an AI-style learning app with a working backend and a simple browser UI.

## Features
- Quiz generation
- Math challenge generation
- Story creation
- Resume summary generation
- Translation helper
- Tutor-style explanations
- Automatic fallback if no API key is configured

## Run locally

1. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Start the app
   ```bash
   uvicorn app:app --reload
   ```

4. Open the browser at
   ```text
   http://localhost:8000
   ```

## Optional: real OpenAI API
Copy `.env.example` to `.env` and add your key:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

If no key is set, the app still works with built-in local fallback responses.
