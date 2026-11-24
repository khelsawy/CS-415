# CS-415 — Agentic AI

CS-415 builds an AI-powered support ticket system one lab at a time. Students start with a Python script that classifies sample tickets, then turn it into a REST API, connect it to large language models (LLMs), and build an agent that answers questions about a customer's stored tickets. Each section preserves its own version of the project so you can run it independently and compare implementations.

By the end of Section 5, you should be able to:

- Represent and process support tickets with Python functions, collections, and type hints.
- Validate data with Pydantic and expose it through a modular FastAPI application.
- Switch LLM providers through configuration, handle streamed replies, and validate model-generated data.
- Build a bounded tool-calling loop that validates tool arguments and passes results back to the model.
- Store tickets in Supabase and explain how customer-scoped queries and short-term chat history support a multi-turn conversation.

## Course progress

| Section | Status | Milestone |
| --- | --- | --- |
| [1](#section-1--python-fundamentals-for-ai-agents) | Complete | Process and summarize tickets in Python. |
| [2](#section-2--pydantic-and-fastapi) | Complete | Classify validated tickets over HTTP. |
| [3](#section-3--modular-ticket-api-and-llm-providers) | Complete | Split the API into modules and add a shared LLM client. |
| [4](#section-4--from-llm-calls-to-ai-agents) | Complete | Generate replies, stream text, and run a tool-calling loop. |
| [5](#section-5--database-backed-ticket-system-and-customer-chat) | Complete | Store tickets and answer customer questions through web and terminal chat. |
| 6 | Not started | |

## Repository structure

```text
CS-415/
├── README.md
├── pyproject.toml              # Project metadata, dependencies, and console command
├── uv.lock                     # Resolved dependency versions
├── .python-version             # Python 3.14
├── .gitignore                  # Ignores local environments and .env files
├── src/cs_415/                 # Package behind the cs-415 greeting command
├── sec-01/
│   └── main.py                 # Python ticket-processing script
├── sec-02/
│   └── main.py                 # Single-file Ticket API
├── sec-03/
│   ├── ticket_api/             # Models, services, routes, and app entry point
│   ├── llm/                    # Shared client, configuration, and providers/
│   ├── examples/               # Package stub
│   └── .env.example            # LLM settings template
├── sec-04/
│   ├── ticket_api/             # Modular classifier API
│   ├── llm/                    # Provider layer with SovereignEG streaming
│   ├── examples/               # Five standalone LLM and agent demos
│   └── .env.example            # LLM settings template
├── sec-05/
│   ├── ticket_api/             # API, classification, and Supabase data access
│   ├── agent/                  # Agent loop, customer-scoped tools, and chat sessions
│   ├── llm/                    # Same provider layer as Section 4
│   ├── web/                    # Login, ticket submission, and chat pages
│   ├── examples/               # Carried-forward agent-loop example from Section 4
│   ├── README.md               # Supabase setup and first run
│   ├── schema.sql              # Tables and backend access for a new lab project
│   ├── seed.sql                # Optional fictional customers and tickets
│   └── .env.example            # LLM and Supabase settings template
├── assignments/                # Written assignment instructions
├── slides/                     # PowerPoint decks for Sections 1–5
└── references/
    └── ollama-colab/           # Setup guide, notebook, test script, and .env template
```

## Technologies and tools

| Technology | Role in the course |
| --- | --- |
| Python 3.14 and uv | Run the labs and manage the shared environment. |
| Pydantic and FastAPI | Validate requests, responses, and tool arguments. Serve REST endpoints and provide interactive Swagger UI. |
| Requests and python-dotenv | Make HTTP requests to LLM providers and load section-specific configuration. |
| Ollama, Google Colab, ngrok, Groq, and SovereignEG | Run models locally or remotely. The Colab reference uses an authenticated HTTPS tunnel through ngrok. |
| Supabase Python client and PostgreSQL | Store and query customers and tickets in Section 5. |
| HTML, CSS, and JavaScript | Implement Section 5's browser forms and chat using the FastAPI backend. |

[pyproject.toml](pyproject.toml) also declares LiteLLM. The section provider adapters make their requests directly with Requests.

## Set up the course project

### 1. Install Python and uv

The project requires Python 3.14 or newer and selects **3.14** in [.python-version](.python-version). On Windows, install the Python install manager, then run `py install 3.14` in PowerShell. On either Windows or Linux, you can have uv install Python after installing uv. [Python downloads](https://www.python.org/downloads/) · [uv guide to installing Python](https://docs.astral.sh/uv/guides/install-python/)

Install uv using the command for your terminal. If `uv` is unavailable after installation, reopen the terminal. [Official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

**Windows PowerShell with WinGet**

```powershell
winget install --id=astral-sh.uv -e
```

**Linux**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you still need Python 3.14, run `uv python install 3.14`.

### 2. Clone the repository and install dependencies

With Git installed, run these commands in the directory where you keep your course projects. They work in PowerShell and Bash.

```text
git clone https://github.com/khelsawy/CS-415.git
cd CS-415
uv sync --locked
uv run python --version
```

`uv sync --locked` uses [uv.lock](uv.lock) to create the project environment. `uv run` runs commands inside that environment automatically. The optional `uv run cs-415` command prints a greeting from [the package entry point](src/cs_415/__init__.py).

### 3. Run a lab

Start each command block at the repository root, the folder containing `pyproject.toml`, unless the instructions say otherwise. Stop a running server with **Ctrl+C** and run `cd ..` if you entered a section folder before starting another block. The lab servers use port 8000 by default, so run them one at a time.

Section 1 and the Section 2–4 HTTP APIs run without provider credentials. Configure an LLM for the Section 4 demos and for Section 5 classification and chat.

### LLM configuration for Sections 3–5

Copy the template for your section to a private `.env` file in the same folder. Edit your existing `.env` if you already have one. [Section 3 template](sec-03/.env.example) · [Section 4 template](sec-04/.env.example) · [Section 5 template](sec-05/.env.example)

For example, to create the Section 5 file from the repository root:

**Windows PowerShell**

```powershell
if (-not (Test-Path sec-05/.env)) { Copy-Item sec-05/.env.example sec-05/.env }
```

**Linux**

```bash
if [ ! -e sec-05/.env ]; then cp sec-05/.env.example sec-05/.env; fi
```

Replace `sec-05` with `sec-03` or `sec-04` when configuring those sections. Set `LLM_PROVIDER` and fill in the variables listed for your connection. The selected model must be available at the configured endpoint.

| `LLM_PROVIDER` | Connection | Required settings |
| --- | --- | --- |
| `ollama_local` | A local Ollama server with the selected model downloaded | `OLLAMA_LOCAL_URL`, `OLLAMA_LOCAL_MODEL` |
| `ollama_colab` | Ollama on Colab through an HTTPS ngrok tunnel with Basic Authentication | `OLLAMA_COLAB_URL`, `OLLAMA_COLAB_MODEL`, `OLLAMA_COLAB_USERNAME`, `OLLAMA_COLAB_PASSWORD` |
| `groq` | Groq chat API | `GROQ_BASE_URL`, `GROQ_MODEL`, `GROQ_API_KEY` |
| `sovereign` | SovereignEG chat API | `SOVEREIGN_BASE_URL`, `SOVEREIGN_MODEL`, `SOVEREIGN_API_KEY` |

Use a base URL. The client appends `/api/chat` for Ollama or `/chat/completions` for Groq and SovereignEG. Each section loads its own `.env`, and variables already set in the terminal take precedence. Keep keys and passwords in your private configuration. Git ignores `.env` files and allows `.env.example` templates.

For Colab, follow the [Ollama + Google Colab guide](references/ollama-colab/README.md). Keep the runtime and tunnel running while you use the local examples. Match `OLLAMA_COLAB_MODEL` to the model loaded in the notebook. The notebook's default profile uses `qwen3.5:4b`, so update the template if you use that profile. The standalone reference script uses its own `OLLAMA_*` settings under `references/ollama-colab/`.

Section 4 Example 01 uses SovereignEG, the provider with an implemented streaming method. Choose a model that supports tool calling for Examples 02–04 and the Section 5 chat. Both agent loops also require each model tool call to include an ID so Python can attach the matching result.

## Section 1 — Python fundamentals for AI agents

Learn to represent ticket data and turn repeated steps into reusable functions. The script covers variables and basic types, strings and f-strings, lists, dictionaries, conditions, loops, and function annotations.

[sec-01/main.py](sec-01/main.py) classifies messages as `billing`, `technical`, or `general` using keywords, sets priority to `high` for urgent tickets and `normal` otherwise, then prints a summary by category.

```text
uv run python sec-01/main.py
```

## Section 2 — Pydantic and FastAPI

Learn to validate incoming data and expose a Python function over HTTP. [sec-02/main.py](sec-02/main.py) defines a `Ticket` input model with minimum text lengths and an optional urgency flag that defaults to `false`. Its `TicketResult` model restricts category and priority to known values. The classifier keeps Section 1's keyword and urgency rules.

```text
uv run fastapi dev sec-02/main.py
```

Open [Swagger UI](http://127.0.0.1:8000/docs), expand `POST /tickets/classify`, select **Try it out**, and submit:

```json
{"customer_name": "Demo Student", "message": "My payment failed", "urgent": true}
```

The response is `{"category":"billing","priority":"high"}`. Try shortening the message to one character to see a validation error. The same request and response apply to the Section 3 and 4 APIs. You can also open the [API status page](http://127.0.0.1:8000/) or [ReDoc](http://127.0.0.1:8000/redoc).

## Section 3 — Modular Ticket API and LLM providers

Learn how to divide a working API into packages and give different providers a shared interface.

- [Models](sec-03/ticket_api/models.py) define the data contracts, [services](sec-03/ticket_api/services.py) contain the classification rules, [routes](sec-03/ticket_api/routes.py) handle HTTP, and [the app](sec-03/ticket_api/main.py) registers the router.
- [LLM configuration](sec-03/llm/config.py) validates environment variables. [LLMClient](sec-03/llm/client.py) selects one of the [provider adapters](sec-03/llm/providers/) and exposes a shared `chat()` method.

```text
cd sec-03
uv run python -m uvicorn ticket_api.main:app --reload
```

Try the Section 2 request in Swagger. This route still uses the Python keyword classifier. The provider layer is available for Python callers, and Section 4 contains the runnable course demos that use it.

## Section 4 — From LLM calls to AI agents

Learn to generate a reply, stream it, describe tools with JSON Schema, validate tool requests, and feed execution results back to a model. The five [examples](sec-04/examples/) use the existing Python classifier and sample tickets held in memory.

| Example | What to look for |
| --- | --- |
| [00 — LLM reply](sec-04/examples/00_ticket_llm_only.py) | Python classifies a sample ticket and the model writes a customer reply. |
| [01 — Streaming](sec-04/examples/01_ticket_streaming.py) | Text fragments print as they arrive. The [SovereignEG adapter](sec-04/llm/providers/sovereign.py) reads server-sent events. |
| [02 — First tool](sec-04/examples/02_ticket_first_tool.py) | The model requests `classify_ticket`. Python validates its arguments with Pydantic, executes the tool, and prints the result. |
| [03 — Multiple tools](sec-04/examples/03_ticket_multi_tools.py) | The model chooses classification, status, or details. Python uses Pydantic-generated schemas and an explicit mapping of allowed handlers. |
| [04 — Agent loop](sec-04/examples/04_ticket_agent_loop.py) | Python sends tool results back with matching `tool_call_id` values and waits for a final answer, with a limit of six model calls. |

Examples 02 and 03 end after tool execution. Example 04 carries its message history across model calls within one run. The slides use that distinction to introduce conversation history, short-term context, and long-term memory.

After configuring `sec-04/.env`, enter the section and run the examples individually. The `-m` form lets Python find the section's sibling packages. The demos run independently of FastAPI.

```text
cd sec-04
uv run python -m examples.00_ticket_llm_only
uv run python -m examples.01_ticket_streaming
uv run python -m examples.02_ticket_first_tool
uv run python -m examples.03_ticket_multi_tools
uv run python -m examples.04_ticket_agent_loop
```

To run the Section 4 HTTP API, run `uv run python -m uvicorn ticket_api.main:app --reload` from `sec-04/`. It exposes the same classification route as Section 3.

## Section 5 — Database-backed ticket system and customer chat

Learn to persist application data, validate model output, and ground a multi-turn chat in customer records. The API replaces keyword matching with LLM-generated JSON for the ticket category. Pydantic accepts only a `category` field with one of the three known values. Python still derives priority from `urgent`. Invalid model output stops ticket creation before the database insert.

| Source | What it implements |
| --- | --- |
| [Routes](sec-05/ticket_api/routes.py) and [models](sec-05/ticket_api/models.py) | HTTP endpoints and input validation for tickets, customers, and chat. |
| [Services](sec-05/ticket_api/services.py) | AI classification, Egyptian mobile number normalization, customer lookup and registration, and ticket operations. |
| [Database client](sec-05/ticket_api/database.py) and [repository](sec-05/ticket_api/repository.py) | Reuse a Supabase client and query the `customers` and `tickets` tables. |
| [Agent loop](sec-05/agent/agent.py) and [tools](sec-05/agent/tools.py) | Require a successful lookup before accepting a final answer. The model can request `get_my_tickets`, `get_my_latest_ticket`, or `get_my_ticket_details`. Python scopes each query to the session's customer ID. |
| [Chat sessions](sec-05/agent/chat_sessions.py) and [web pages](sec-05/web/) | Tie a session ID to a customer and keep successful user and assistant turns in server memory. FastAPI serves the HTML, CSS, and JavaScript. |

Customers and tickets are stored in PostgreSQL and survive server restarts. Chat history lasts for the current in-memory session. Reloading the chat page starts a new session, and restarting the server clears its sessions.

### Configure Supabase

Follow the [Section 5 setup guide](sec-05/README.md) to create your own Supabase project, run [schema.sql](sec-05/schema.sql), and optionally load [fictional customers and tickets](sec-05/seed.sql). Copy the [environment template](sec-05/.env.example) to `sec-05/.env`, then fill in `SUPABASE_URL`, `SUPABASE_KEY`, and the settings for your LLM provider.

Use fictional customer data in a local classroom environment. The demo identifies customers by phone number without verifying ownership, and the general ticket routes lack customer-level authentication.

### Run the browser demo

```text
cd sec-05
uv run python -m uvicorn ticket_api.main:app --reload
```

1. Open the [login page](http://127.0.0.1:8000/login). Use a classroom test number in an accepted Egyptian mobile format, such as `01xxxxxxxxx` or its `+201xxxxxxxxx` form. The service accepts mobile prefixes `010`, `011`, `012`, and `015`.
2. If the number is new, enter a test name to register. The browser then opens the [chat page](http://127.0.0.1:8000/chat).
3. Open [Create Ticket](http://127.0.0.1:8000/create-ticket) from chat. Submit a message such as “I was charged twice for my subscription.” Check the returned ticket ID, category, priority, and status.
4. Return to chat and ask “What is my latest ticket?” Then ask “What is the status of that ticket?” The agent uses the session history for context and queries the database for ticket facts.

Open [Swagger UI](http://127.0.0.1:8000/docs) to try the same backend operations directly.

| Requests | Purpose |
| --- | --- |
| `GET /` | Confirm the API is running. Works without a provider or database connection. |
| `POST /tickets/classify` | Classify a ticket without saving it. Requires an LLM, and works with the same input shape as Section 2. |
| `POST /tickets`, `GET /tickets`, `GET /tickets/{ticket_id}`, `PATCH /tickets/{ticket_id}/status` | Create, list, retrieve, or change the status of stored tickets. Valid statuses are `open`, `in_progress`, `resolved`, and `closed`. |
| `POST /customers/lookup`, `POST /customers/register`, `POST /customers/tickets` | Identify or register a customer and submit a ticket linked to that customer. |
| `POST /chat/sessions`, `POST /chat/message` | Start a session with a known customer's phone number, then send messages with the returned session ID. |

### Run the terminal agent

From the repository root:

```text
cd sec-05
uv run python -m agent.agent
```

Enter the phone number of an existing demo customer, then ask about their tickets. Type `exit` or `quit` to stop. The terminal agent uses the same Supabase data and provider settings as the browser demo and runs independently of the web server.

For a standalone recap, run `uv run python -m examples.04_ticket_agent_loop` from `sec-05/`. The [sample-ticket agent loop](sec-05/examples/04_ticket_agent_loop.py) looks up one fictional ticket in memory and calls the Section 5 LLM classifier. It only needs LLM settings.

## Assignments and supporting materials

- The [assignments folder](assignments/) contains [Assignment 01 — Modular Programming & Ollama API](assignments/assignment-01.md). It asks you to modularize the Section 2 API and write a Python client for local Ollama or Ollama Cloud. The assignment page contains submission instructions and the deadline.
- Section 4's slides include an exercise to add streaming for Groq and both Ollama modes. Section 5's instructor deck includes a walkthrough and practice tasks for ticket creation and customer chat.
- The [Ollama + Colab setup guide](references/ollama-colab/README.md) walks through the [notebook](references/ollama-colab/Ollama_Colab.ipynb) and the [local test client](references/ollama-colab/test_ollama.py). After configuring the reference client's own [.env template](references/ollama-colab/.env.example), run `uv run python references/ollama-colab/test_ollama.py` from the repository root.

### Slides

The [slides folder](slides/) contains the PowerPoint decks for each lab.

- [Section 1 — Python Fundamentals for AI Agents](slides/CS415_Lab1_Python_Fundamentals_for_AI_Agents_v2.pptx)
- [Section 2 — Pydantic and FastAPI for AI Agents](slides/CS415_Lab2_Pydantic_FastAPI_for_AI_Agents.pptx)
- [Section 3 — Modular Ticket API and LLM Providers](slides/CS415_Lab03_Modular_Ticket_API_and_LLM_Providers.pptx)
- [Section 4 — From LLM Calls to AI Agents](slides/CS415_Lab04_From_LLM_Calls_to_AI_Agents.pptx)
- [Section 5 — Real Ticket System (instructor deck)](slides/CS415_Lab05_Real_Ticket_System_Instructor_Deck.pptx)

**Instructor** · Mohamed Elsawy
