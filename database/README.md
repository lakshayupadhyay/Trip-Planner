# Database — Supabase

This folder contains all database-related files for the Personalized Travel Itinerary Planner.

## Contents (to be added in Epic 2)

| File/Folder | Purpose |
|---|---|
| `schema.sql` | Table definitions (users, itineraries, destinations, etc.) |
| `migrations/` | Version-controlled schema changes |
| `seed.sql` | Sample data for local development and testing |
| `rls_policies.sql` | Row Level Security policies for Supabase |

## Supabase Setup (Epic 2)

1. Create a free project at [supabase.com](https://supabase.com)
2. Copy your Project URL and anon key into `.env`
3. Run `schema.sql` in the Supabase SQL editor
4. Apply RLS policies from `rls_policies.sql`

> **Never commit real Supabase credentials.** Use `.env` (git-ignored) for secrets.

