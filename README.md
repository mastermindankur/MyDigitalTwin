
---
title: MyDigitalTwin
app_file: app.py
sdk: gradio
sdk_version: 5.31.0
---
# MyDigitalTwin

AI-powered virtual assistant for Ankur Khera using OpenAI, Gradio, and web scraping. Answers questions based on website content, logs user interest and unknown queries, and sends real-time push notifications via Pushover.

# Ankur Khera Virtual Assistant

This is a virtual assistant designed for Ankur Khera, hosted at [ankurkhera.online](https://ankurkhera.online). It uses OpenAI-compatible APIs and website scraping to answer questions about Ankur’s work, background, and interests. The assistant is built using FastAPI and Gradio, with logging and alerting features.

## Features

- Scrapes content from https://ankurkhera.online for context-based responses.
- Utilizes OpenAI-compatible (Gemini-style) endpoints for generation.
- Logs unknown or new user questions with timestamps.
- Includes a form for users to express interest in connecting with Ankur.
- Sends real-time alerts using the Pushover API.
- Deployable via a Gradio interface.

## Local Setup (Using `uv`)

1. Clone the repository:

   ```bash
   git clone https://github.com/mastermindankur/MyDigitalTwin.git
   cd ankur-assistant
   ```

2. Install `uv` if not already installed:

   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```

3. Sync the environment and install dependencies:

   ```bash
   uv sync
   ```

4. Create a `.env` file in the root directory with the following environment variables:

   ```
   OPENAI_API_KEY=your_openai_api_key
   GEMINI_API_KEY=your_openai_compatible_key
   PUSHOVER_USER=your_pushover_user_key
   PUSHOVER_TOKEN=your_pushover_app_token
   HF_TOKEN=your_huggingface_token
   ```

   Alternatively, set these variables on your server or environment.

5. Run the app locally:

   ```bash
   uv run app.py
   ```

## Deployment on Hugging Face Spaces

1. In the "Secrets" section of your Hugging Face Space, add the following environment variables:

   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
   - `PUSHOVER_USER`
   - `PUSHOVER_TOKEN`
   - `HF_TOKEN`

2. Deploy using:

   ```bash
   uv run gradio deploy
   ```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
