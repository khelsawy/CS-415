# Assignment 01: Modular Programming & Ollama API

**Deadline:** Before the next lab session.

## Part 1: Code Modularization

### Objective

Refactor the FastAPI application from Section 02 into a modular Python project.

### Requirements

1. Split `sec-02/main.py` into separate Python modules.
2. Each module must have a clear responsibility.
3. Separate Pydantic models, API routes, and application logic.
4. Use Python imports to connect the modules.
5. Keep `main.py` as the application entry point.
6. Preserve all existing functionality.
7. Make sure all API endpoints still work.

You are free to choose your own project structure.

### Verification

Run the FastAPI application:

```bash
uv run fastapi dev sec-02/main.py
```

Open http://127.0.0.1:8000/docs and verify that all endpoints work correctly.

---

## Part 2: Ollama API Integration

### Objective

Build a Python application that communicates with a Large Language Model (LLM) using the Ollama API.

### Requirements

1. Use Ollama to interact with any LLM of your choice.
2. You can choose ONE of the following approaches:

   **Option A: Local Model**
   - Install Ollama.
   - Download and run any supported LLM locally.
   - Communicate with the model using the local Ollama API.

   **Option B: Ollama Cloud**
   - Create an account on Ollama.
   - Generate an Ollama API Key.
   - Use any available cloud model.
   - Communicate with the model using the Ollama Cloud API.
   - No model download is required.

3. Write Python code that:
   - Sends a prompt to the selected model through an API.
   - Receives the model's response.
   - Extracts the generated text.
   - Displays the response.

### API Information

**Local Ollama API:**

http://localhost:11434/api/chat

**Ollama Cloud API:**

https://ollama.com/api/chat

Cloud requests require an API Key.

### Important Rules

- Both local and cloud models are accepted.
- Downloading a model is OPTIONAL.
- Model interaction MUST happen programmatically through an API.
- Using the terminal to interact directly with the model
  is NOT accepted.
- You may use any Python HTTP library.
- Never include API Keys directly in your source code.
- Never upload API Keys to GitHub.

### References

- https://ollama.com
- https://docs.ollama.com/cloud
- https://docs.ollama.com/api



## Submission Requirements

Submit:

1. Your refactored Section 02 Python code.
2. Your Python script demonstrating Ollama API communication.
3. A short README explaining:
   - Your module organization.
   - Which LLM you selected.
   - Whether you used Local Ollama or Ollama Cloud.
   - How to run your code.

## General Instructions

- Complete both parts before the next lab session.
- Make sure your code runs successfully.
- Be prepared to explain your implementation during the lab.