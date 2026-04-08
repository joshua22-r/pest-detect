#!/bin/bash
# Build script for Render

# Install backend dependencies
pip install -r backend/requirements.txt

# Run Django migrations
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
cd ..

# Install frontend dependencies and build
npm install
npm run build
