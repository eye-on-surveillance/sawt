-- feedback cards
create table "public"."feedback_cards" (
    "id" uuid not null default gen_random_uuid(),
    "title" text,
    "question_id" bigint,
    "card_type" text,
    "citations" jsonb,
    "responses" jsonb,
    "k" bigint
);





-- user feedback

create table "public"."user_feedback" (
    "created_at" timestamp with time zone not null default now(),
    "user_id" text,
    "comment" jsonb,
    "question_id" bigint,
    "response_id" uuid,
    "accuracy" integer,
    "helpfulness" integer,
    "balance" integer
);




alter table "public"."user_feedback" add column "id" uuid not null default gen_random_uuid();

CREATE UNIQUE INDEX feedback_cards_id_key ON public.feedback_cards USING btree (id);

CREATE UNIQUE INDEX feedback_cards_pkey ON public.feedback_cards USING btree (id);

CREATE UNIQUE INDEX user_feedback_pkey ON public.user_feedback USING btree (id);

alter table "public"."feedback_cards" add constraint "feedback_cards_pkey" PRIMARY KEY using index "feedback_cards_pkey";

alter table "public"."user_feedback" add constraint "user_feedback_pkey" PRIMARY KEY using index "user_feedback_pkey";

alter table "public"."feedback_cards" add constraint "feedback_cards_id_key" UNIQUE using index "feedback_cards_id_key";

alter table "public"."feedback_cards" enable row level security;


create policy "Enable insert access for all users"
on "public"."feedback_cards"
as permissive
for insert
to public
with check (true);


create policy "Enable read access for all users"
on "public"."feedback_cards"
as permissive
for select
to public
using (true);


create policy "Enable update access for all users"
on "public"."feedback_cards"
as permissive
for update
to public
using (true)
with check (true);

alter table "public"."user_feedback" enable row level security;

create policy "anyone can insert"
on "public"."user_feedback"
as permissive
for insert
to public
with check (true);


create policy "anyone can read"
on "public"."user_feedback"
as permissive
for select
to public
using (true);


create policy "anyone can update"
on "public"."user_feedback"
as permissive
for update
to public
using (true)
with check (true);