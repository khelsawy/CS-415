# CS-415 — Agentic AI

## Course Overview

CS-415 introduces Agentic AI through practical Python development. The course uses one continuous project: the **AI-Powered Support Ticket System**. Students extend the same system across labs, moving from Python functions to validated APIs, LLM-generated replies, tools, and an agent loop.

Each `sec-XX` directory contains that lab's version of the project so students can compare the stages.

## Course Progress

Labs 01–04 are complete.

| Lab | Topic | What it adds to the Ticket System |
|---|---|---|
| [Lab 01](sec-01/main.py) | Python Fundamentals, Functions, Type Hints | Represents tickets with dictionaries, classifies messages, assigns priorities, and prints summaries using functions and loops. |
| [Lab 02](sec-02/main.py) | Pydantic and FastAPI | Validates ticket input and classification output, then exposes the classifier through an HTTP API. |
| [Lab 03](sec-03/) | Modular Ticket API and LLM Providers | Separates models, services, and routes; adds configuration and a common client for four LLM connection modes. |
| [Lab 04](sec-04/) | LLM Integration, Streaming, Tool Calling, Multiple Tools, and Agent Loop | Adds five standalone examples that progress from generating a reply to selecting tools and returning their results to the model. |

The Lab 03 and Lab 04 HTTP APIs retain the deterministic classification behavior from Lab 02. The Lab 04 LLM demonstrations run separately and call Python services directly; they do not require a running FastAPI server.

## Repository Structure

This simplified tree omits package marker files (`__init__.py`) and expands Lab 04 in more detail.

```text
CS-415/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── src/cs_415/                 # Minimal project entry point
├── sec-01/
│   └── main.py                 # Python fundamentals and ticket processing
├── sec-02/
│   └── main.py                 # Single-file Pydantic + FastAPI application
├── sec-03/
│   ├── ticket_api/             # Modular models, services, routes, and app
│   ├── llm/                    # Client, configuration, and providers/
│   ├── examples/               # Package marker only; no runnable examples
│   └── .env.example
├── sec-04/
│   ├── ticket_api/
│   │   ├── models.py           # Pydantic input/output models
│   │   ├── services.py         # Deterministic classification rules
│   │   ├── routes.py           # HTTP endpoints
│   │   └── main.py             # FastAPI app and router registration
│   ├── llm/
│   │   ├── config.py           # Load section-specific provider settings
│   │   ├── client.py           # Shared chat and streaming interfaces
│   │   └── providers/
│   │       ├── ollama.py       # Local and Colab connections
│   │       ├── groq.py
│   │       └── sovereign.py
│   ├── examples/
│   │   ├── 00_ticket_llm_only.py
│   │   ├── 01_ticket_streaming.py
│   │   ├── 02_ticket_first_tool.py
│   │   ├── 03_ticket_multi_tools.py
│   │   └── 04_ticket_agent_loop.py
│   └── .env.example
├── slides/                    # PowerPoint presentations for Labs 01–04
├── assignments/
│   └── assignment-01.md
└── references/
    └── ollama-colab/           # Setup guide, notebook, test client, env template
```

`ticket_api/` owns ticket validation, business rules, and HTTP routing. `llm/` provides the application's model interface, while `llm/providers/` handles provider-specific requests, authentication, and responses. `examples/` demonstrates how to combine these pieces.

## Prerequisites and Installation

Before starting, install:

- **Python 3.14 or newer**, as required by [pyproject.toml](pyproject.toml). [.python-version](.python-version) selects **3.14** for this project.
- **uv**, the Python project and dependency manager. It must be available as `uv` in your terminal.
- **Git** to clone the repository.
- **VS Code** as the recommended editor.

From the directory where you keep your course projects:

```bash
git clone https://github.com/khelsawy/CS-415.git
cd CS-415
uv sync
```

`uv sync` creates the project virtual environment and installs dependencies from the project configuration and lockfile. These include FastAPI with its standard tools, Pydantic, Requests, python-dotenv, and LiteLLM. The current provider implementations use Requests. Use `uv run` for the commands below; manual virtual environment activation is unnecessary.

## Running the Labs

Each command block in this section starts at the **repository root** (the directory containing `pyproject.toml`). If you have entered a section directory, run `cd ..` before starting another block.

### Lab 01: Python fundamentals

```bash
uv run python sec-01/main.py
```

This prints the Python demonstrations, ticket classifications, priorities, and summary counts.

### Lab 02: Single-file Ticket API

```bash
uv run fastapi dev sec-02/main.py
```

### Lab 03: Modular Ticket API

```bash
cd sec-03
uv run python -m uvicorn ticket_api.main:app --reload
```

### Lab 04: Modular Ticket API

```bash
cd sec-04
uv run python -m uvicorn ticket_api.main:app --reload
```

Run one server at a time on the default port, 8000. For Labs 02–04, open:

- [API status](http://127.0.0.1:8000/)
- [Swagger UI](http://127.0.0.1:8000/docs) to try `POST /tickets/classify`
- [ReDoc](http://127.0.0.1:8000/redoc) for API documentation

For example, submit this body in Swagger UI:

```json
{"customer_name": "Ahmed", "message": "My payment failed", "urgent": true}
```

The classifier returns `{"category": "billing", "priority": "high"}`. No LLM configuration is needed for these API endpoints. Stop the server with `Ctrl+C`.

For the Lab 04 LLM examples, configure a provider below, then follow the **Lab 04 Examples** commands.

## LLM Providers

Labs 03 and 04 contain three provider implementations supporting four connection modes:

| Connection mode | `LLM_PROVIDER` | Connection and settings required |
|---|---|---|
| Ollama Local | `ollama_local` | Ollama running on your computer with the selected model downloaded; set `OLLAMA_LOCAL_URL` and `OLLAMA_LOCAL_MODEL`. |
| Ollama on Google Colab | `ollama_colab` | Ollama running in Colab behind an HTTPS ngrok tunnel with Basic Authentication; set `OLLAMA_COLAB_URL`, `OLLAMA_COLAB_MODEL`, `OLLAMA_COLAB_USERNAME`, and `OLLAMA_COLAB_PASSWORD`. |
| Groq | `groq` | Hosted chat API; set `GROQ_BASE_URL`, `GROQ_MODEL`, and `GROQ_API_KEY`. |
| SovereignEG | `sovereign` | Hosted chat API; set `SOVEREIGN_BASE_URL`, `SOVEREIGN_MODEL`, and `SOVEREIGN_API_KEY`. |

### Configuration

Use the template for the section you are running: [Lab 03 .env.example](sec-03/.env.example) or [Lab 04 .env.example](sec-04/.env.example). From the repository root, create the private configuration for Lab 04 **only if it does not already exist**:

```bash
cp sec-04/.env.example sec-04/.env
```

On Windows PowerShell, use:

```powershell
Copy-Item sec-04/.env.example sec-04/.env
```

For Lab 03, replace `sec-04` with `sec-03` in the copy command. Edit an existing `.env` instead of overwriting it.

In that section's `.env`, set `LLM_PROVIDER` to one of the exact values in the table and fill in the selected provider's settings. Unused provider credentials can remain empty. Both templates initially select `ollama_colab` and contain placeholders, so they need configuration before use. For the streaming example, select `LLM_PROVIDER=sovereign` and supply your SovereignEG settings.

Each section loads its own `.env` using a path relative to `llm/config.py`; a root-level `.env` is not the configured file. Existing process environment variables take precedence over values in that file. Keep API keys and passwords private and out of version control.

For Colab, follow the [Ollama + Google Colab guide](references/ollama-colab/README.md). Keep the runtime and tunnel running while using the examples. Copy the protected HTTPS URL and API credentials into the section's `OLLAMA_COLAB_*` variables. The reference test client uses different names (`OLLAMA_URL`, `OLLAMA_MODEL`, etc.) in its own configuration. Match the section's model to the one actually downloaded: the section template uses `gpt-oss:120b`, while the notebook's default profile uses `qwen3.5:4b`.

### Client and provider responsibilities

- **`LLMConfig`** is a frozen dataclass holding the selected provider, model, base URL, and authentication settings. `load_config()` checks required environment values and constructs it.
- **`LLMClient`** selects a provider and exposes `chat(messages, tools=None)`, returning an assistant-message dictionary. Lab 04 also exposes `chat_stream(messages)`, which yields text fragments.
- **Provider implementations** send HTTP requests and extract assistant messages. Ollama uses `/api/chat`; Groq and SovereignEG use `/chat/completions` under their configured base URLs.

### Chat, streaming, and tool compatibility

| Connection mode | `chat()` in Labs 03 and 04 | `chat_stream()` in Lab 04 |
|---|---|---|
| Ollama Local | Implemented | Not implemented |
| Ollama on Colab | Implemented | Not implemented |
| Groq | Implemented | Not implemented |
| SovereignEG | Implemented | Implemented using Server-Sent Events (SSE) |

Lab 03 has no streaming interface. In Lab 04, choosing a provider without `chat_stream()` raises `NotImplementedError`; the client does not silently fall back to a non-streaming reply.

All providers accept optional tool definitions, but successful tool calling depends on the selected model and its response format. Example 04 requires a nonempty `id` on every returned tool call so it can send a matching `tool_call_id`. It stops if an ID is missing. The providers return tool calls without adding missing IDs, so basic chat support alone does not guarantee agent-loop compatibility.

## Lab 04 Examples

Configure `sec-04/.env` first. From the repository root, enter the section once:

```bash
cd sec-04
```

Run all commands below from **`sec-04/`**. Use `python -m` so Python can find the sibling `ticket_api` and `llm` packages. Each example runs independently and makes real requests to the configured model; no API server needs to be started.

### 00 — LLM-generated reply

[00_ticket_llm_only.py](sec-04/examples/00_ticket_llm_only.py) adds an AI-written customer response to the existing classifier. Python first determines category and priority, then sends those results and the sample ticket to `chat()` and prints the complete reply.

```bash
uv run python -m examples.00_ticket_llm_only
```

### 01 — Streaming

[01_ticket_streaming.py](sec-04/examples/01_ticket_streaming.py) keeps classification in Python and changes reply delivery: `chat_stream()` prints fragments as they arrive. Compared with Example 00, students learn incremental output. **This example currently requires SovereignEG.**

```bash
uv run python -m examples.01_ticket_streaming
```

### 02 — First tool call

[02_ticket_first_tool.py](sec-04/examples/02_ticket_first_tool.py) introduces a tool schema and lets the LLM request classification. It uses a fixed sample ticket with `customer_name="Ahmed"`, `message="I cannot login to my account"`, and `urgent=True`. Python validates the requested arguments with `Ticket`, runs the allowed classifier, and prints the result. This moves from direct classification to model-requested execution using `chat()`; it does not send the tool result back to the model yet.

```bash
uv run python -m examples.02_ticket_first_tool
```

### 03 — Multiple tools

[03_ticket_multi_tools.py](sec-04/examples/03_ticket_multi_tools.py) expands the single tool into `classify_ticket`, `get_ticket_status`, and `get_ticket_details`. Students learn Pydantic-generated schemas, tool selection, and dispatch through explicit handler and input-model mappings. Three independent prompts use a temporary in-memory store containing tickets 1 and 2. Results are printed but are still not returned to the LLM.

```bash
uv run python -m examples.03_ticket_multi_tools
```

### 04 — Agent loop

[04_ticket_agent_loop.py](sec-04/examples/04_ticket_agent_loop.py) adds the missing feedback step: it appends tool results to the conversation and calls the model again. It asks for ticket 1's customer name, status, category, and priority, using a single in-memory sample ticket. The model can request further tools before answering. `MAX_TOOL_ROUNDS = 6` caps the loop at six model calls; reaching the limit can end the run without a final answer.

```bash
uv run python -m examples.04_ticket_agent_loop
```

## Important Architectural Concepts

- **Deterministic classification vs generated responses:** Python checks message keywords to choose `billing`, `technical`, or `general`, and uses `urgent` to choose `high` or `normal` priority. The same validated input produces the same result. LLM-generated wording and tool choices can vary.
- **Tool definition vs execution:** A tool definition describes a name, purpose, and JSON argument schema. Sending it does not execute a function. The LLM requests an action; Python decides whether to run the named handler.
- **Pydantic validation:** Model-generated arguments are external input. The examples parse JSON arguments when needed and validate them with `Ticket` or `TicketIdInput` before dispatch. These models enforce constraints such as minimum text lengths and positive ticket IDs.
- **Multiple tool selection and dispatch:** `TOOL_HANDLERS` maps allowed names to Python functions, and `TOOL_INPUT_MODELS` maps names to their argument models. An unknown tool name is rejected rather than executed.
- **Returning results to the LLM:** Example 04 appends the assistant's tool requests, followed by JSON tool results in messages with `role="tool"`. Each result's `tool_call_id` links it to the original request. Tool errors are also returned as JSON so the model can respond to them.
- **Bounded agent loop:** The cycle is model request → validated tool execution → tool result → next model request. It finishes when the model returns without requesting tools, or stops at the iteration limit. The limit bounds repeated calls; it does not guarantee task completion.

## Memory Concepts

Lab 04 concludes with a theoretical introduction to three related ideas:

| Concept | Meaning |
|---|---|
| Conversation History | The ordered record of user messages, assistant responses, and tool interactions. |
| Short-Term Memory | Context needed for the current task, such as recent history, an active ticket ID, or recent tool results. |
| Long-Term Memory | Information deliberately stored and retrieved for later tasks or conversations, such as a saved customer preference. |

Example 04 keeps a local `messages` list during one `run_agent()` call and includes it in subsequent model requests. Example 03 starts a new message list for each question. The sample ticket stores exist only in process memory and are not persistent agent memory.

**Persistent Agent Memory has not been implemented in the Lab 04 examples.** There is no saved conversation history or cross-session memory, and the agent does not remember users across independent sessions.

## Student Exercise: Multi-Provider Streaming

SovereignEG streaming is implemented in [sec-04/llm/providers/sovereign.py](sec-04/llm/providers/sovereign.py). Extend the Lab 04 provider layer with equivalent streaming support for:

- **Groq:** implement `chat_stream(messages)` to yield generated text fragments.
- **Ollama Local / Colab:** implement streaming in their shared `OllamaProvider`, retaining the correct connection and authentication behavior for each mode.

Preserve the existing `chat(messages, tools=None)` interface, tool-calling behavior, and Ticket System functionality. The existing Example 01 should work with each newly supported provider through the same `LLMClient.chat_stream()` interface.

This practical exercise is presented in the Lab 04 slides; there is no separate assignment file for it in `assignments/`.

## Course Materials

### Presentations

The [slides directory](slides/) contains:

- [Lab 01 — Python Fundamentals for AI Agents](slides/CS415_Lab1_Python_Fundamentals_for_AI_Agents_v2.pptx)
- [Lab 02 — Pydantic and FastAPI for AI Agents](slides/CS415_Lab2_Pydantic_FastAPI_for_AI_Agents.pptx)
- [Lab 03 — Modular Ticket API and LLM Providers](slides/CS415_Lab03_Modular_Ticket_API_and_LLM_Providers.pptx)
- [Lab 04 — From LLM Calls to AI Agents](slides/CS415_Lab04_From_LLM_Calls_to_AI_Agents.pptx)

### Assignments

The [assignments directory](assignments/) currently contains [Assignment 01 — Modular Programming & Ollama API](assignments/assignment-01.md). It asks students to modularize the Lab 02 application and write an Ollama API client. See the file for submission requirements and its stated deadline, “before the next lab session.”

### References

The [references directory](references/) contains the Ollama + Google Colab materials:

- [Setup guide](references/ollama-colab/README.md)
- [Colab notebook](references/ollama-colab/Ollama_Colab.ipynb)
- [Standalone local test client](references/ollama-colab/test_ollama.py)
- [Reference client configuration template](references/ollama-colab/.env.example)

## Instructor

Mohamed Elsawy
