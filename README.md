# CS 415 - Agentic AI

Welcome to the CS 415 course repository.

This repository contains the code and practical examples covered in our lab sessions.

## Course Topics

- Python for AI Agents
- Functions and Type Hints
- Pydantic
- FastAPI
- AI Agents and Tools

## Lab Sessions

| Section | Topics | Folder |
|---------|--------|--------|
| Section 01 | Python Basics & AI Agent Functions | [sec-01](sec-01/) |
| Section 02 | Pydantic & FastAPI | [sec-02](sec-02/) |

## Requirements

Before starting, make sure you have installed:

- Python 3.14+
- uv
- VS Code (recommended)
- Git

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/khelsawy/CS-415.git
```

### 2. Open the Project

```bash
cd CS-415
```

### 3. Install Dependencies

```bash
uv sync
```

This command automatically creates the virtual environment and installs the required dependencies.

## Running Sections

### Section 01 - Python Basics & AI Agent Functions

Run the Python script:

```bash
uv run python sec-01/main.py
```

### Section 02 - Pydantic & FastAPI

Start the FastAPI development server:

```bash
uv run fastapi dev sec-02/main.py
```

Once the server is running, open:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

To stop the server, press `Ctrl + C`.

## Dependencies

The project uses:

- Pydantic
- FastAPI
- Uvicorn (included with FastAPI Standard)

All dependencies are managed using uv.

## Updating the Repository

To get the latest sections and examples:

```bash
git pull origin main
```

To synchronize dependencies after pulling updates:

```bash
uv sync
```
## PowerPoint Slides

All lab presentations are available in the [slides](slides/) folder.

Download the PowerPoint presentations to review the concepts explained during each lab session.


## Assignments

| Assignment | Topics | Deadline |
|------------|--------|----------|
| [Assignment 01](assignments/assignment-01.md) | Code Modularization & Ollama API | Before the next lab |

## Instructor

Mohamed Elsawy
