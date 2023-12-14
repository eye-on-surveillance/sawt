alter table "public"."feedback_cards" add column "model_version" text;

update feedback_cards
set
  model_version = 'v0.0.1';

alter table "public"."feedback_cards" alter column "model_version" set not null;
