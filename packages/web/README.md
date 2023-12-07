This NextJS website let's users query The Great Inquirer (TGI) API.

## Getting Started

Create a `.env.local` like this:

```
# If running functions locally
NEXT_PUBLIC_TGI_API_ENDPOINT=http://localhost:8080

# Run against staging
NEXT_PUBLIC_TGI_API_ENDPOINT=https://us-east1-the-great-inquirer.cloudfunctions.net/getanswer-staging

# All environments
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

## Migration instructions

To make changes to the schema moving forward, you can update the DB directly from Supabase DB. When ready, run `supabase db remote commit`. You will need to have Docker running locally for this to succeed. When complete, there will be a new file in `supabase/migrations` with a name like `20230821153353_remote_commit.sql`. Commit this file to source control and it will automatically be applied to the DB when merged.

### New project

```bash
# from nextjs project
cd packages/web

# connect to project
supabase link --project-ref weqbsjuunfkxuyhsutzx

# sync project with existing migrations
supabase db push

# pull remote project changes to local code
supabase db remote commit
```

This will create a new file in `packages/web/supabase/migrations`. For some reason, Supabase adds a bunch of junk that you can remove from the generated migration.

```sql
-- delete all this
alter table "auth"."saml_relay_states" add column "flow_state_id" uuid;

alter table "auth"."sessions" add column "ip" inet;

alter table "auth"."sessions" add column "refreshed_at" timestamp without time zone;

alter table "auth"."sessions" add column "user_agent" text;

CREATE INDEX flow_state_created_at_idx ON auth.flow_state USING btree (created_at DESC);

CREATE INDEX mfa_challenge_created_at_idx ON auth.mfa_challenges USING btree (created_at DESC);

CREATE INDEX mfa_factors_user_id_idx ON auth.mfa_factors USING btree (user_id);

CREATE INDEX refresh_tokens_updated_at_idx ON auth.refresh_tokens USING btree (updated_at DESC);

CREATE INDEX saml_relay_states_created_at_idx ON auth.saml_relay_states USING btree (created_at DESC);

CREATE INDEX sessions_not_after_idx ON auth.sessions USING btree (not_after DESC);

alter table "auth"."saml_relay_states" add constraint "saml_relay_states_flow_state_id_fkey" FOREIGN KEY (flow_state_id) REFERENCES auth.flow_state(id) ON DELETE CASCADE not valid;

alter table "auth"."saml_relay_states" validate constraint "saml_relay_states_flow_state_id_fkey";
```

## Importing large data

Increase session timeout: `alter role authenticator set statement_timeout = '120s';`
