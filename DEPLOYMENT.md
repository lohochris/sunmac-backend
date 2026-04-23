# SUNMAC Deployment Guide

## Environment Setup

1. Clone the repository
2. Create virtual environment: `python -m venv env`
3. Activate: `env\Scripts\activate` (Windows) or `source env/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your values
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Collect static files: `python manage.py collectstatic`
9. Run server: `python manage.py runserver`

## Required API Keys

- **Groq API Key** - For AI math solving (get from https://console.groq.com)
- **YouTube API Key** - For video search (get from Google Cloud Console)

## Environment Variables

See `.env.example` for all required variables.

## Security Notes

- Never commit `.env` file
- Keep API keys secure
- Use different keys for development and production
- Set `DEBUG=False` in production
- Use proper database in production