This NextJS website let's users query The Great Inquirer (TGI) API.

## Getting Started

Create a `.env.local` like this:

```
# If running functions locally
NEXT_PUBLIC_TGI_API_ENDPOINT=http://localhost:8080

# Run against production
NEXT_PUBLIC_TGI_API_ENDPOINT=https://getanswer-q5odwl64qa-ue.a.run.app

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
