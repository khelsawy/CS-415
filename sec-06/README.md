# Section 6 — Persistent AI agent memory

In this lab you will store multiple conversations per customer in Supabase, reopen a saved transcript after a server restart, and compare the complete transcript with the short history sent to the model. You will also trace how Python decides when a reply needs fresh ticket data.

Section 5 stored browser chat in FastAPI process memory and offered a separate interactive terminal chat. Section 6 uses persistent conversation IDs and focuses on the browser application. The standalone [agent-loop recap](examples/04_ticket_agent_loop.py) remains available for reviewing tool calling.

## 1. Set up Supabase

Use a classroom project with fictional data. Enable the Data API and expose the `public` schema. Open the Supabase SQL Editor and run each required file once.

| Starting point | SQL files to run |
| --- | --- |
| Fresh project | Run [schema.sql](schema.sql) to create customers and tickets, then [memory_schema.sql](memory_schema.sql) to create conversations and messages. |
| Existing Section 5 project | Run only [memory_schema.sql](memory_schema.sql). It adds the two memory tables and preserves existing customers and tickets. |
| Section 6 memory tables already installed | Keep the existing tables and data. Install the memory schema only when both tables are absent. |

Optionally run [seed.sql](seed.sql) for fictional customers and tickets. Alternatively, register a fictional customer in the browser. Check for all four tables in the Table Editor. Section 5 chat was stored in the running process. Section 6 starts with an empty conversation list for each customer.

| Table | Purpose |
| --- | --- |
| `public.conversations` | One row per chat. A generated UUID identifies the conversation. `customer_id` is required and references `customers.id`. An index supports listing a customer's newest conversations. |
| `public.messages` | One row per user or assistant message. A generated `bigint` ID establishes display order. The required foreign key references the conversation and cascades on conversation deletion. Role is limited to `user` and `assistant`. Content must be nonempty. An index supports ordered message reads for a conversation. |

The memory schema enables row-level security and grants the backend's `service_role` select and insert access to both tables and usage on the message identity sequence. It grants no direct access to browser roles. The backend uses an elevated key, so the service code checks customer ownership itself.

## 2. Configure and run the browser app

Complete the [course setup](../README.md#set-up-the-course-project). From the repository root, create `sec-06/.env` from [the environment template](.env.example) if the file is absent.

**Linux**

```bash
if [ ! -e sec-06/.env ]; then cp sec-06/.env.example sec-06/.env; fi
```

**Windows PowerShell**

```powershell
if (-not (Test-Path sec-06/.env)) { Copy-Item sec-06/.env.example sec-06/.env }
```

Set `SUPABASE_URL` to the project URL and `SUPABASE_KEY` to the backend Secret key for that project. Keep this file private. Configure one [LLM provider](../README.md#llm-configuration-for-sections-36) and select a model that supports tool calling. The agent matches each tool call to its result by ID. The Ollama adapter supplies an ID when the native API omits one.

From the repository root:

```text
cd sec-06
uv run python -m uvicorn ticket_api.main:app --reload
```

Open [the login page](http://127.0.0.1:8000/login). With the seed data, use `01000000000` for Demo Customer A or `01100000000` for Demo Customer B. The chat sidebar lists up to the 50 newest conversations and opens the newest on page load. Select **New Chat** to create a separate conversation or choose an existing conversation to display its saved messages. **Create Ticket** continues to use the existing ticket service.

From the `sec-06` directory, run the standalone recap with `uv run python -m examples.04_ticket_agent_loop`. It uses a fictional in-memory ticket and needs only LLM settings.

## 3. Follow the memory flow

1. The browser sends the classroom phone number to FastAPI. The [conversation service](ticket_api/conversation_service.py) resolves the customer in Supabase. For transcript reads and sends, it verifies the conversation ID belongs to that customer before accessing messages.
2. The [conversation repository](ticket_api/conversation_repository.py) reads and writes using the server-side Supabase client. The transcript endpoint reads all saved messages in ascending ID order, paging through the results. The sidebar can reopen a conversation in a new FastAPI process because the records are in Supabase.
3. For a new message, [Sliding Window Memory](agent/memory.py) loads at most 20 previous message rows by reading the newest first and reversing them for the prompt. In ordinary sequential use, that is up to **10 completed user/assistant turns**. The agent also receives the current question. As the window advances, older turns remain in the browser transcript and in storage. This is a count limit, so a long turn can still use many tokens.
4. The [agent](agent/agent.py) first classifies the current question and recent history as needing a ticket lookup or ordinary conversation. Python validates that decision. Invalid routing output falls back to requiring a lookup. If a lookup is required or the reply model requests a tool, Python accepts a final reply only after a valid result from the customer-scoped tool allowlist. A confirmed empty list or missing ticket counts as a valid result. Tool errors do not count.
5. The service saves a nonblank answer and its question in one bulk insert. Failed or empty replies create no completed turn. System prompts, tool requests, and tool results are used during the turn and are not saved as transcript rows.
6. The browser [chat script](web/chat.js) adds both messages to the transcript only after a successful API response and keeps the input available after an error. Loading, creating, and sending cannot overlap in one chat page. If a network failure leaves the outcome uncertain, reopen the conversation and check the transcript before trying again.

### Conversation API

All four routes accept JSON via POST. Use [Swagger UI](http://127.0.0.1:8000/docs) to inspect the request models.

| Route | Request fields | Result |
| --- | --- | --- |
| `/conversations` | `phone` | Creates a conversation. Returns HTTP 201 with `conversation_id`, `customer_name`, and `created_at`. |
| `/conversations/list` | `phone` | Returns the customer's newest conversation rows. |
| `/conversations/history` | `phone`, `conversation_id` | Returns the complete saved transcript in order. |
| `/conversations/message` | `phone`, `conversation_id`, `message` | Saves a completed turn and returns `conversation_id` and `answer`. |

Conversation IDs must be UUIDs. An absent or unowned conversation returns 404. An empty, whitespace-only, or over-4,000-character message returns 422. An unavailable or unusable model reply can return 503 without saving a turn.

## 4. Verify a restart

1. Start a new chat and say “Hello. My demo color is violet.” Ask “What color did I mention?” Both replies should work without reading a ticket.
2. With the seed data for Demo Customer A, ask “What is my latest ticket?” Then ask “What is its priority?” Expect the sign-in ticket and a fresh lookup for the follow-up. Ask “What did I ask you just before this?” to practice transcript recall.
3. Create a second chat. Switch between the two conversations and confirm their transcripts are separate.
4. Stop FastAPI with **Ctrl+C**. Start it again with the same command and Supabase project. Reload `/chat`, select the first conversation, and check that its transcript is visible and a recent follow-up still works.
5. Send more than 10 completed turns in one conversation. Confirm that older messages remain visible. Ask about an early detail that was never repeated in the recent turns and compare the answer with the visible transcript.
6. In Swagger, try to load Demo Customer A's conversation using Demo Customer B's fictional number. Expect 404. Try a malformed UUID and an empty message. Expect 422.
7. To check failed message recovery with a local Ollama setup, stop Ollama while leaving FastAPI running. Send a message and check that the draft stays in the input and the transcript stays unchanged. Restart Ollama and send the draft again.

## 5. Lab limits

- Phone checks are classroom identification and provide no proof of ownership. Use fictional data and keep the server on localhost. The general ticket endpoints have no customer-level authentication. Production use would require authenticated identities and an authorization policy for every route.
- The configured LLM provider receives recent transcript text and any ticket data returned by tools. Keep credentials and personal information out of chats and tickets. The backend key belongs in `.env` on the server, outside browser assets and version control.
- The model makes an extra request to classify each turn. A well-formed but incorrect classification can route a ticket question as ordinary chat, particularly for ambiguous phrasing or context outside the window. The Python guard verifies that a scoped lookup succeeded when required and does not verify that every sentence is supported by the retrieved result.
- Tabs and workers may process turns for the same conversation simultaneously. Requests may use the same history, and completed message pairs have no separate turn ID to guarantee adjacency under concurrent writes. The 10-turn count assumes sequential use. There is no request deduplication. If the server saves a turn but the reply is lost, a manual resend can create another turn.
- Full transcript retrieval reads every saved message. The agent window is based on row count, and the lab assumes that the Data API allows at least 20 rows per response. There is no token budgeting or transcript retention policy.
