# Section 5 — Supabase setup and first run

Use a new Supabase project and fictional customer data for this lab. The FastAPI app uses phone numbers for classroom identification and runs on your computer. Keep the app on localhost and the Supabase secret in the backend's `.env`.

## 1. Create the database

1. Create a project in the Supabase Dashboard. Leave the **Data API** enabled and make sure `public` is an exposed schema under **Integrations → Data API**. [Supabase Data API setup](https://supabase.com/docs/guides/api/creating-routes)
2. Open **SQL Editor** in your new project. Start a new query, copy in all of [schema.sql](schema.sql), and choose **Run**. Run this file once in a new project.
3. To start with sample customer records, open a separate query, copy in [seed.sql](seed.sql), and choose **Run**. You can skip this step and register a test customer in the web app.
4. In **Table Editor**, check that `public.customers` and `public.tickets` are present. If you loaded the seed data, you should see two customers and three tickets in a fresh database.

Customers have UUIDs and unique phone numbers in normalized Egyptian mobile format. Tickets have generated integer IDs, classification fields, a status that defaults to `open`, and timestamps. The optional `customer_id` links a ticket to its owner. The general `POST /tickets` endpoint can create an unlinked ticket, while the browser creates customer-linked tickets. The slides mention a nullable `auth_user_id` column in the instructor database. The app never reads or writes it, so the lab schema omits it.

Both tables enable Row Level Security (RLS). The schema grants access for the backend's `service_role` and leaves direct Data API access blocked for browser roles. Ticket and customer rows persist across app restarts. Chat sessions stay in the FastAPI process.

## 2. Configure the local app

Complete the [course setup](../README.md#set-up-the-course-project) and copy [the environment template](.env.example) to `sec-05/.env`. From the repository root, use the command for your shell. If you already have the file, edit it in place.

**Windows PowerShell**

```powershell
if (-not (Test-Path sec-05/.env)) { Copy-Item sec-05/.env.example sec-05/.env }
```

**Linux**

```bash
if [ ! -e sec-05/.env ]; then cp sec-05/.env.example sec-05/.env; fi
```

- Set `SUPABASE_URL` to the **Project URL** shown in the project's **Connect** dialog. Use the base HTTPS URL.
- Set `SUPABASE_KEY` to a **Secret key** from **Settings → API Keys**. The Python backend needs elevated database access. Keep this value in `sec-05/.env`, out of the browser files and Git. [Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys)
- Set `LLM_PROVIDER` and its required variables following the [course provider instructions](../README.md#llm-configuration-for-sections-35). The template selects local Ollama. Start Ollama and install the configured model if you keep that selection. Choose a tool-capable model for chat.

## 3. Run a smoke check

From the repository root:

```text
cd sec-05
uv run python -m uvicorn ticket_api.main:app --reload
```

1. Open [the API status page](http://127.0.0.1:8000/). For a database-only check, use [Swagger UI](http://127.0.0.1:8000/docs) to try `GET /tickets`. Expect the seeded rows if you ran the seed file, or an empty list in a fresh project without seed data.
2. Open [the login page](http://127.0.0.1:8000/login). If you seeded the database, enter demo number `01000000000` for Demo Customer A or `01100000000` for Demo Customer B. Without seed data, enter a fictional number in the expected format and follow the registration prompt.
3. For Demo Customer A, ask “What is my latest ticket?” before adding any tickets. The latest seeded ticket is the sign-in issue with status `in_progress`. Follow up with “What is its priority?” and check that the answer uses the same ticket.
4. Use **Create Ticket** to submit a fictional problem. Check the returned ID, category, priority, and status. Restart the server and use `GET /tickets` to see that the record persists.

If the database check fails, verify that the URL and secret come from the same project, that the Data API is enabled, and that the schema ran successfully there. If the database works but classification or chat fails, check the model and provider settings. The agent needs tool-call IDs from the provider to match database results to tool requests.

See the [Section 5 overview](../README.md#section-5--database-backed-ticket-system-and-customer-chat) for the terminal demo and endpoint list.
