# HaggLab Website

The website of HaggLab, a software and AI studio. It presents 5 services and 10 projects, and every project has a
Try it page where visitors use the working tool on sample data.

Stack: Python 3.12+, Django 6.1, PostgreSQL (Neon), plain HTML/CSS/JS, Gunicorn + WhiteNoise.
AI: Google Gemini and Hero's AI (fallback chain), Pinecone for document search (RAG).

---

## 1. Run it locally

```powershell
# 1. Activate the virtual environment (it lives one folder up)
..\venv\Scripts\activate

# 2. Install packages (requirements-dev.txt adds local-only tools)
pip install -r requirements-dev.txt

# 3. Copy .env.example to .env and fill in the values you have.
#    Leave NEON_DB_HOST empty to use the local db.sqlite3 instead of Neon.

# 4. Create the tables and the starting content (services, projects, FAQs, Fiverr gigs)
python manage.py migrate
python manage.py seed_content

# 5. Start the site
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin is at `/manage-studio/` (or your `ADMIN_URL_PATH`).

Local runs use `config.settings.dev`: every project is shown, rate limits and the daily AI limit are off, and
each AI call is printed step by step in the terminal (`AI_TRACE`).

---

## 2. How it is organised

| Folder | What is in it |
|---|---|
| `apps/core` | Page views, the 404/500 pages, Fiverr switch (`fiverr.py`) |
| `apps/content` | Services, projects, FAQs, settings and Fiverr gigs (models + admin), `seed_content` command |
| `apps/tryit` | The Try it tools: `specs.py` (inputs), `engines.py` (calculations), `hero_client.py` (AI chain), `prompts.py` + `system_prompts.py`, `rag.py` (Pinecone), `usage.py` (daily AI limit), `analysis/` (pandas sandbox, reports, forecasts) |
| `apps/leads` | Start a project form, inquiry emails (`notify.py`), Fiverr visitor detection |
| `apps/analytics`, `apps/security` | First-party page analytics, security headers |
| `templates/`, `static/` | HTML templates, CSS (`tokens.css`, `site.css`) and JS |
| `datasets/` | Fictional sample data used by the Try it pages |

**AI chain** (`apps/tryit/hero_client.py`): Gemini key 1 → Hero 1 → Gemini 2 → Hero 2 → Hero 3. A key that is
over its limit or slow rests for 2 minutes at the end of the chain.

**Calculation tools** (InsightDesk, ReportBot, ForecastBoard, BookIt) calculate in Python; the AI only writes code
(InsightDesk, run in a sandbox) or explains the numbers.

**Document search:** after changing a dataset, re-upload it with `python manage.py rag_ingest [project]`.

---

## 3. Checks before a commit or deploy

```powershell
python manage.py test apps                 # all tests
python scripts/check_design_rules.py       # design rules
pip-audit                                  # known package vulnerabilities
python manage.py send_test_email           # inquiry email reaches OWNER_EMAIL
```

Production settings check (needs the production values in the environment):

```powershell
python manage.py check --deploy --settings=config.settings.prod
```

---

## 4. Deploying

- Set `DJANGO_SETTINGS_MODULE=config.settings.prod` on the server (`config/wsgi.py` defaults to dev).
- Production refuses to start without `SECRET_KEY`, `ALLOWED_HOSTS`, the Neon values, Turnstile keys,
  `OWNER_EMAIL` and the `EMAIL_*` SMTP values.
- After each upload: `pip install -r requirements.txt`, `python manage.py migrate`,
  `python manage.py collectstatic --noinput`.
- Start command (see `Procfile`): `gunicorn config.wsgi:application --timeout 120 --workers 2`.
  The long timeout is needed because Hero's AI can take 25–40 seconds.
- Disk: the installed packages need about 160 MB (pandas and numpy are most of it).

---

## 5. Environment variables

All secrets come from environment variables. `.env.example` lists every name the code reads. Never commit real
values or the `.env` file.

---

## 6. Older standalone demos

`demos/` holds three early standalone versions (DocuMind, InsightDesk, ShopAssist) with their own `manage.py`
and `run_eval` commands. The website does not use them; the Try it pages in `apps/tryit` replaced them.
