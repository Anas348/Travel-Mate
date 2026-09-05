# ✈️ TravelMate — Smart Travel & Destination Guide

A hotel search and destination guide for Pakistan — search hotels by city,
budget, and rating, read reviews and amenities, browse destination guides
with nearby attractions, and add your own hotel or destination listing.

Originally a database-systems coursework project; rebuilt with a full
redesign, real accounts, and a database layer that runs anywhere —
including a one-click deploy to [Vercel](https://vercel.com).

## Group

**Group 17** — Anas Malik (24P-0652) · Manahil Fatima (24P-0527) · Asawir Binte Asif (24P-0576)

## Features

- 🔍 Search hotels by city, max budget, and minimum rating
- 🏨 Hotel pages with room types, amenities, nearby attractions, and reviews
- ⭐ Leave and edit your own reviews (with real login — not a hardcoded user)
- ❤️ Save hotels to a personal favourites list
- 🌍 Destination guides with attractions per valley/city
- ➕ **Add your own hotel or destination** — any logged-in visitor can list a
  place, not just the original authors
- 📋 "My listings" page to see what you've added

## Tech stack

- **Backend:** Flask (Python)
- **Database:** SQLAlchemy models — the *same* code creates the schema on
  SQLite, PostgreSQL, or MySQL. Which one you use is just an environment
  variable (see below).
- **Frontend:** Jinja2 templates, hand-written CSS (no framework), a little
  vanilla JS for the mobile menu and repeatable form rows.
- **Deployment target:** Vercel (serverless Python), config included.

## Project structure

```
travelmate/
├── app.py                # Flask app: routes, auth, everything the site does
├── models.py             # SQLAlchemy models — the schema, in one place
├── config.py             # Reads SECRET_KEY / DATABASE_URL from the environment
├── seed.py               # Creates tables + loads sample data (any DB backend)
├── requirements.txt
├── vercel.json            # Vercel build/routing config
├── api/index.py           # Vercel's serverless entry point (imports app.py)
├── .env.example           # Copy to .env for local dev
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/              # All pages
└── sql/legacy_mysql_schema.sql   # The original hand-written MySQL schema, kept for reference
```

## Quick start (local development)

Requires Python 3.10+.

```bash
git clone <your-repo-url>
cd travelmate

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY if you like

python seed.py                  # creates travelmate.db (SQLite) and loads sample data
python app.py                   # http://127.0.0.1:5000
```

**Demo accounts** (created by `seed.py`, password `1234` for both):
- `anas@gmail.com` — regular traveler account
- `ali@gmail.com` — admin account (can edit any review, not just their own)

No MySQL server, no manual `CREATE TABLE` statements — `seed.py` builds the
database from `models.py` the first time you run it.

## Working with the database

Everything about the schema lives in **`models.py`**. There's no separate
`.sql` file to keep in sync — whichever database `DATABASE_URL` points at,
`db.create_all()` builds the same tables from those model classes. This is
what makes switching databases a config change instead of a rewrite.

### Adding more data

Three ways, depending on who's adding it:

1. **As a site visitor** — this is the actual feature: log in (or register)
   and use **"Add a hotel"** or **"Add a destination"** in the nav bar. This
   is how anyone other than the original developers adds real data, with no
   code or database access needed.
2. **As the maintainer, permanently** — open `seed.py`, add rows to the
   `hotels_data`, `destinations_data`, etc. lists near the top, then run:
   ```bash
   python seed.py --reset
   ```
   `--reset` drops and recreates every table before reseeding, so use it
   for the local/dev database only — never against a live database with
   real user submissions in it.
3. **Ad hoc, from a Python shell** — for one-off inserts without touching
   `seed.py`:
   ```bash
   python
   >>> from app import app
   >>> from models import db, Hotel
   >>> with app.app_context():
   ...     db.session.add(Hotel(name="New Hotel", city="Lahore", price_per_night=15000))
   ...     db.session.commit()
   ```

### Switching to a different database provider

By default, `DATABASE_URL` is unset and the app falls back to a local
SQLite file (`travelmate.db`) — zero setup, great for developing locally.
**Don't use SQLite for the live Vercel deployment** — Vercel's serverless
functions have a read-only filesystem outside of `/tmp`, and `/tmp` doesn't
persist between requests, so any data written to a SQLite file would
disappear. For the deployed site, point `DATABASE_URL` at a real hosted
database instead:

**Option A — PostgreSQL (recommended, e.g. [Neon](https://neon.tech) or [Supabase](https://supabase.com), both have a free tier):**
1. Create a free project on either service.
2. Copy the connection string they give you (starts with `postgresql://` or `postgres://`).
3. Set it as `DATABASE_URL` — locally in `.env`, or in Vercel's Project
   Settings → Environment Variables for the live site.
4. `psycopg2-binary` is already in `requirements.txt`, so no extra install
   is needed.

**Option B — MySQL** (e.g. a MySQL instance you host elsewhere — Vercel
itself can't run a MySQL server, so this needs an external provider that
accepts remote connections):
1. Set `DATABASE_URL` to a URL like
   `mysql+mysqlconnector://user:password@host:3306/dbname`.
2. `mysql-connector-python` is already in `requirements.txt`.

Either way, the code in `app.py` and `models.py` doesn't change — only the
`DATABASE_URL` value and, if needed, which driver is installed.

After pointing `DATABASE_URL` at a fresh hosted database, run
`python seed.py` **once from your local machine** (with that same
`DATABASE_URL` in your `.env`) to create the tables and load the starter
hotels/destinations before real users start adding their own.

## Deploying to Vercel

1. Push this project to a GitHub (or GitLab/Bitbucket) repository.
2. On [vercel.com](https://vercel.com), click **Add New → Project** and
   import that repository. Vercel will detect `vercel.json` automatically —
   no build command needed.
3. Before deploying, add these under **Project Settings → Environment
   Variables**:
   - `SECRET_KEY` — any long random string
   - `DATABASE_URL` — your hosted Postgres (or MySQL) connection string
     from the section above. **Do not leave this unset in production** —
     without it, the app falls back to SQLite, which won't save data on
     Vercel.
4. Deploy. Vercel builds `api/index.py` as a Python serverless function and
   serves everything under `/static` directly.
5. Run `python seed.py` locally once (pointed at the same `DATABASE_URL`)
   to load the starter data into the live database, if you haven't already.
6. Visit the URL Vercel gives you — that's the live site.

Redeploys after this are automatic on every push to your main branch.

## Security notes

This started as a coursework project, so a few things are simplified on
purpose: there's no email verification, no password reset flow, and no
rate limiting on login attempts. Passwords are hashed (not stored in
plaintext, unlike the original version), but treat this as a demo/learning
project rather than production-hardened software before using it for
anything real.

## Database tables

`users` · `hotels` · `rooms` · `favourites` · `destinations` · `attractions`
· `reviews` · `amenities` · `hotel_amenity` — all defined in `models.py`.
