# Deploying HaggLab on AlwaysData (free plan)

The free plan gives 1 GB disk, 256 MB RAM and ¼ CPU. The site needs about 160 MB of disk and about 170 MB of
RAM at its busiest, so it fits, with **one** Gunicorn worker (4 threads). Do not raise the worker count.

Below, replace `ACCOUNT` with your AlwaysData account name. Your site address will be
`https://ACCOUNT.alwaysdata.net`.

> If Heros already runs on the same AlwaysData account, both apps share the same 256 MB of RAM.
> Use a separate free account for HaggLab.

---

## 1. Before you start

- Push the code to GitHub: `git push -u origin main`
- Have your `.env` values ready. You will type them on the server, never commit them.

## 2. Choose Python

In the AlwaysData admin: **Environment > Python** and set the default version to **3.12** (or 3.13).

## 3. Open a terminal on the server (SSH)

1. **Remote access > SSH**: edit the SSH user and turn on **password login**.
2. On your computer:
   ```
   ssh ACCOUNT@ssh-ACCOUNT.alwaysdata.net
   ```

## 4. Get the code and install packages

```bash
git clone https://github.com/Hudsonmathew1910/HaggLab.git ~/hagglab
cd ~/hagglab
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5. Create the production .env on the server

```bash
nano ~/hagglab/.env
```

Paste your values (same names as `.env.example`). Production-specific ones:

| Name | Value |
|---|---|
| `SECRET_KEY` | A **new** long random value (see below), not the one from your computer |
| `ALLOWED_HOSTS` | `ACCOUNT.alwaysdata.net` |
| `SITE_URL` | `https://ACCOUNT.alwaysdata.net` |
| `ADMIN_URL_PATH` | A hard-to-guess path, for example `studio-desk-7k2/` |
| `AI_DAILY_CAP` | `300` |
| `NEON_DB_*`, `EMAIL_*`, `OWNER_EMAIL`, `TURNSTILE_*`, `GEMINI_*`, `HEROS_*`, `PINECONE_*` | Same as your local `.env` |

Make a new secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
Save with Ctrl+O, Enter, Ctrl+X. Then lock the file so only you can read it:
```bash
chmod 600 ~/hagglab/.env
```

In **Cloudflare Turnstile**, add `ACCOUNT.alwaysdata.net` to the allowed hostnames of your widget, or the
contact form's spam check will fail.

## 6. Use the production settings in the terminal

```bash
echo 'export DJANGO_SETTINGS_MODULE=config.settings.prod' >> ~/.profile
source ~/.profile
```

## 7. Prepare the site

```bash
cd ~/hagglab && source venv/bin/activate
python manage.py check --deploy          # should say: no issues
python manage.py migrate                 # Neon is already up to date; this is safe to run
python manage.py collectstatic --noinput
python manage.py send_test_email         # a test email should reach OWNER_EMAIL
```

Your admin user already exists in Neon. Only if you need a new one: `python manage.py createsuperuser`.

## 8. Create the site

**Web > Sites > Add a site**

| Field | Value |
|---|---|
| Addresses | `ACCOUNT.alwaysdata.net` |
| Type | **User program** |
| Command | `/home/ACCOUNT/hagglab/venv/bin/gunicorn config.wsgi:application --bind [::]:$PORT --workers 1 --threads 4 --timeout 120` |
| Working directory | `/home/ACCOUNT/hagglab` |
| Environment | `DJANGO_SETTINGS_MODULE=config.settings.prod` |

In the site's **SSL** tab, turn on **Force HTTPS**. Save. AlwaysData starts the site.

## 9. Check it

- `https://ACCOUNT.alwaysdata.net/` and `/health/` (should show `{"status": "ok"}`)
- A wrong address, for example `/xyz/`, shows the HaggLab 404 page
- One Try it page per kind: DocuMind, InsightDesk, ReportBot, BookIt
- Send the Start a project form once and check the email arrives
- Log in at `/ADMIN_URL_PATH`

## 10. Updating the site later

```bash
cd ~/hagglab && source venv/bin/activate
git pull
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then **Web > Sites > (your site) > Restart**.

---

## If something goes wrong

| What you see | Likely cause |
|---|---|
| Site does not start | Look at the logs in `~/admin/logs/sites/`. A `RuntimeError` names the missing `.env` value |
| "Bad Request (400)" | `ALLOWED_HOSTS` does not match the address |
| "Too many redirects" | HTTPS detection. Tell Claude; `SECURE_PROXY_SSL_HEADER` may need a change |
| "CSRF verification failed" on a form | `SITE_URL` must be exactly `https://ACCOUNT.alwaysdata.net` |
| Pages have no styling | Run `collectstatic` again and restart |
| Try it says "busy" | AI keys or quota; check the logs |
| Site restarts or is killed under load | Memory: make sure the command has `--workers 1` |
