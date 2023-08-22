
create table "public"."cards" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "title" text not null,
    "subtitle" text,
    "likes" bigint not null default '0'::bigint,
    "status" text not null default 'new'::text,
    "card_type" text not null,
    "responses" jsonb not null default '[]'::jsonb,
    "citations" jsonb not null default '[]'::jsonb,
    "processing_time_ms" integer
);


alter table "public"."cards" enable row level security;

CREATE UNIQUE INDEX card_pkey ON public.cards USING btree (id);

alter table "public"."cards" add constraint "card_pkey" PRIMARY KEY using index "card_pkey";

create policy "anyone can insert"
on "public"."cards"
as permissive
for insert
to public
with check (true);


create policy "anyone can read"
on "public"."cards"
as permissive
for select
to public
using (true);


create policy "anyone can update"
on "public"."cards"
as permissive
for update
to public
using (true)
with check (true);

