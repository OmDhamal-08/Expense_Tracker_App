#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Seed predefined categories + payment methods (safe to run multiple times)
python manage.py seed_defaults

# Automatically create a superuser if environment variables are set
if [[ -n "${DJANGO_SUPERUSER_USERNAME}" && -n "${DJANGO_SUPERUSER_PASSWORD}" && -n "${DJANGO_SUPERUSER_EMAIL}" ]]; then
  python manage.py createsuperuser --noinput || true
fi
