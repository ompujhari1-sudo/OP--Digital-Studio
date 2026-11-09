# OP Digital Studio

Premium portfolio and enquiry website built with Flask.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Enable contact form email delivery

The contact form sends enquiries to `ompujhari.digital@gmail.com` using Gmail SMTP.

1. Turn on 2-Step Verification for the Google account that owns the inbox.
2. Create a Google App Password from the account's App Passwords settings.
3. Copy `.env.example` to `.env` and set `SMTP_USER`, `SMTP_APP_PASSWORD`, and a strong `SECRET_KEY`.
4. Load those variables into your local shell or use a dotenv loader. Never commit `.env` or share the app password in chat.
5. The app automatically reads the local `.env` file. For deployment, add the same values in the hosting provider's Environment Variables settings.

`SMTP_APP_PASSWORD` is a Google App Password, not your normal Gmail password. If SMTP is not configured, the form shows a clear message and the email link remains available.

## Deploy

Use a Python web service with:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Add `SECRET_KEY`, `SMTP_USER`, and `SMTP_APP_PASSWORD` as private environment variables in the hosting dashboard.
