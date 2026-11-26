-- Run once in a new Supabase project before applying memory_schema.sql.
begin;

create table public.customers (
    id uuid primary key default gen_random_uuid(),
    phone text not null unique check (phone ~ '^\+201[0125][0-9]{8}$'),
    customer_name text not null
);

create table public.tickets (
    id bigint generated always as identity primary key,
    customer_id uuid references public.customers (id),
    customer_name text not null check (char_length(customer_name) >= 2),
    message text not null check (char_length(message) >= 5),
    urgent boolean not null default false,
    category text not null check (category in ('billing', 'technical', 'general')),
    priority text not null check (priority in ('high', 'normal')),
    status text not null default 'open'
        check (status in ('open', 'in_progress', 'resolved', 'closed')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- The FastAPI backend uses a server-side key. Browser clients have no direct table access.
alter table public.customers enable row level security;
alter table public.tickets enable row level security;

revoke all on table public.customers, public.tickets from public, anon, authenticated, service_role;
revoke all on sequence public.tickets_id_seq from public, anon, authenticated, service_role;

grant usage on schema public to service_role;
grant select, insert on table public.customers to service_role;
grant select, insert, update on table public.tickets to service_role;
grant usage on sequence public.tickets_id_seq to service_role;

commit;
