-- Run once after schema.sql or on a compatible Section 5 project.
begin;

create table public.conversations (
    id uuid primary key default gen_random_uuid(),

    customer_id uuid not null
        references public.customers(id),

    created_at timestamptz not null default now()
);


create table public.messages (
    id bigint generated always as identity primary key,

    conversation_id uuid not null
        references public.conversations(id)
        on delete cascade,

    role text not null
        check (role in ('user', 'assistant')),

    content text not null
        check (char_length(trim(content)) > 0),

    created_at timestamptz not null default now()
);


create index idx_conversations_customer
on public.conversations(customer_id, created_at, id);

create index idx_messages_conversation
on public.messages(conversation_id, id);


alter table public.conversations
enable row level security;

alter table public.messages
enable row level security;


revoke all on table
    public.conversations,
    public.messages
from public, anon, authenticated, service_role;

revoke all on sequence public.messages_id_seq
from public, anon, authenticated, service_role;


grant select, insert on table
    public.conversations,
    public.messages
to service_role;

grant usage on sequence public.messages_id_seq
to service_role;

commit;
