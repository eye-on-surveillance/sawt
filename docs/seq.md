seqdiag {
User-Browser -> Vercel-NextJS [label = "GET SITE JS"];
User-Browser <-- Vercel-NextJS
User-Browser -> Supabase [label = "GET CARD DATA"];
User-Browser <-- Supabase
User-Browser -> Google-Cloud-Function [label = "SUBMIT QUESTION"]
User-Browser <-- Google-Cloud-Function
User-Browser -> Supabase [label = "SUBMIT NEW CARD"];
User-Browser <-- Supabase
}
