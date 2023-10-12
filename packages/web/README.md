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

### Supabase migrations

The first time you setup a new Supabase project, migrations must be applied.

```
supabase login
supabase link --project-ref $PROJECT_ID
supabase db push
```

To make changes to the schema moving forward, you can update the DB directly from Supabase DB. When ready, run `supabase db remote commit`. You will need to have Docker running locally for this to succeed. When complete, there will be a new file in `supabase/migrations` with a name like `20230821153353_remote_commit.sql`. Commit this file to source control and it will automatically be applied to the DB when merged.
