-- Optional classroom records. Run after schema.sql in your new lab project.
begin;

insert into public.customers (phone, customer_name)
values
    ('+201000000000', 'Demo Customer A'),
    ('+201100000000', 'Demo Customer B')
on conflict (phone) do nothing;

insert into public.tickets (
    customer_id, customer_name, message, urgent, category, priority, status, created_at
)
select c.id, c.customer_name, s.message, s.urgent, s.category, s.priority, s.status, s.created_at
from (
    values
        ('+201000000000', 'I was charged twice for my subscription.', false,
            'billing', 'normal', 'resolved', now() - interval '2 days'),
        ('+201000000000', 'I cannot sign in to the demo portal.', true,
            'technical', 'high', 'in_progress', now() - interval '1 day'),
        ('+201100000000', 'Where can I find the user guide?', false,
            'general', 'normal', 'open', now() - interval '1 day')
) as s (phone, message, urgent, category, priority, status, created_at)
join public.customers as c on c.phone = s.phone
where not exists (
    select 1
    from public.tickets as t
    where t.customer_id = c.id and t.message = s.message
);

commit;
