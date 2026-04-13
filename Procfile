release: cd backend && python manage.py migrate && python manage.py collectstatic --noinput --clear && python manage.py shell < seed_data.py
web: cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 1
web: cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
