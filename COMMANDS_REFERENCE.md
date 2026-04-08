# Commands Reference Card

Quick reference for all important commands.

---

## Backend Commands

### Setup & Initialization
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Management
```bash
# Create migrations
python manage.py makemigrations api

# Apply migrations
python manage.py migrate

# Seed test data
python manage.py shell < seed_data.py

# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py shell < seed_data.py
```

### Running Server
```bash
# Start on default port 8000
python manage.py runserver 8000

# Start on different port
python manage.py runserver 8001

# Create superuser
python manage.py createsuperuser
```

### Django Admin
```bash
# Access admin panel
http://localhost:8000/admin
# Default: admin / admin123
```

---

## Frontend Commands

### Setup & Dependencies
```bash
# Navigate to project root
cd ..

# Install dependencies
npm install
# or
pnpm install

# Create env file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

### Running Dev Server
```bash
# Default port 3000
npm run dev

# Custom port
npm run dev -- -p 3001
```

### Building for Production
```bash
# Build
npm run build

# Run production build
npm start

# Lint code
npm run lint
```

---

## API Testing (curl)

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Get Current User (with token)
```bash
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Upload Image for Detection
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "subject_type=plant"
```

### Get Detection History
```bash
curl -X GET http://localhost:8000/api/detections/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Plant Diseases
```bash
curl -X GET http://localhost:8000/api/diseases/plant_diseases/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Animal Diseases
```bash
curl -X GET http://localhost:8000/api/diseases/animal_diseases/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get System Stats
```bash
curl -X GET http://localhost:8000/api/statistics/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Admin Stats (admin only)
```bash
curl -X GET http://localhost:8000/api/admin/stats/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Environment Setup

### Create .env.local
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

### View .env.local
```bash
cat .env.local
```

### Update Backend URL
```bash
echo "NEXT_PUBLIC_API_URL=https://api.example.com/api" > .env.local
```

---

## Troubleshooting Commands

### Kill Process on Port 8000 (macOS/Linux)
```bash
lsof -ti:8000 | xargs kill -9
```

### Kill Process on Port 8000 (Windows)
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Kill Process on Port 3000 (macOS/Linux)
```bash
lsof -ti:3000 | xargs kill -9
```

### Clear npm Cache
```bash
npm cache clean --force
```

### Clear pip Cache
```bash
pip cache purge
```

### Reinstall Dependencies
```bash
# Frontend
rm -rf node_modules package-lock.json
npm install

# Backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Check Python Version
```bash
python --version
# Should be 3.8+
```

### Check Node Version
```bash
node --version
# Should be 16+
```

---

## Database Commands

### SQLite Commands (from bash)
```bash
# View database
sqlite3 backend/db.sqlite3

# In sqlite3 shell:
.tables                    # List all tables
.schema                    # View schema
SELECT * FROM api_user;    # View users
SELECT * FROM api_disease; # View diseases
.exit                      # Exit
```

### Django ORM Shell
```bash
python manage.py shell

# In Python shell:
from api.models import User, Disease
User.objects.all()
Disease.objects.count()
exit()
```

---

## Deployment Commands

### Collect Static Files
```bash
cd backend
python manage.py collectstatic --noinput
```

### Run with Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Run with uWSGI
```bash
uwsgi --http :8000 --wsgi-file config/wsgi.py --master --processes 4 --threads 2
```

### Build Next.js for Production
```bash
npm run build
npm start
```

---

## Git Commands (if using version control)

### Initialize Repository
```bash
git init
```

### Add All Changes
```bash
git add .
```

### Commit Changes
```bash
git commit -m "Your message"
```

### View Status
```bash
git status
```

### View Log
```bash
git log --oneline
```

---

## Useful Shortcuts

### Backend (from backend folder)
```bash
# Quick setup one-liner
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py shell < seed_data.py && python manage.py runserver 8000

# Short commands
alias runserver='python manage.py runserver'
alias makemig='python manage.py makemigrations'
alias migrate='python manage.py migrate'
```

### Frontend (from project root)
```bash
# Short commands
alias dev='npm run dev'
alias build='npm run build'
alias start='npm start'
```

---

## Documentation Access

### View README
```bash
cat README.md
```

### View Setup Guide
```bash
cat QUICKSTART_SETUP.md
```

### View Integration Guide
```bash
cat DJANGO_INTEGRATION.md
```

### View Backend Setup
```bash
cat backend/SETUP.md
```

---

## Useful URLs

### Development
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin
- API Schema: http://localhost:8000/api/

### Pages
- Login: http://localhost:3000/auth/login
- Register: http://localhost:3000/auth/register
- Detect: http://localhost:3000/predict
- History: http://localhost:3000/history
- Profile: http://localhost:3000/profile
- Admin: http://localhost:3000/admin/dashboard

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | `python manage.py runserver 8001` |
| Module not found | `pip install -r requirements.txt` |
| Database locked | `rm db.sqlite3 && python manage.py migrate` |
| CORS error | Check CORS_ALLOWED_ORIGINS in settings |
| Token error | Clear storage and login again |
| API not found | Check NEXT_PUBLIC_API_URL in .env.local |

---

## Advanced Commands

### Python Virtual Environment Management
```bash
# List all environments
python -m venv --help

# Upgrade pip in venv
python -m pip install --upgrade pip

# Check installed packages
pip list

# Show package details
pip show django
```

### Django Management
```bash
# Run tests
python manage.py test

# Check database
python manage.py dbshell

# Flush database (delete all data)
python manage.py flush

# Create admin user
python manage.py createsuperuser

# Change password
python manage.py changepassword username
```

### Node.js Commands
```bash
# Check npm version
npm --version

# Update npm
npm install -g npm@latest

# List installed packages
npm list

# Check for outdated packages
npm outdated

# Update packages
npm update
```

---

## Performance Monitoring

### Django Debug Toolbar (optional, if installed)
```python
# Add to INSTALLED_APPS in settings.py
'debug_toolbar',

# Add to MIDDLEWARE
'debug_toolbar.middleware.DebugToolbarMiddleware',

# Access at: http://localhost:8000/__debug__/
```

### Monitor API Response Time
```bash
time curl http://localhost:8000/api/diseases/
```

### Monitor Frontend Build
```bash
npm run build -- --profile
```

---

## Backup & Recovery

### Backup Database
```bash
cp backend/db.sqlite3 backend/db.sqlite3.backup
```

### Restore Database
```bash
cp backend/db.sqlite3.backup backend/db.sqlite3
```

### Backup Settings
```bash
cp backend/config/settings.py backend/config/settings.py.backup
```

---

## Clean Slate Commands

### Start Fresh - Backend
```bash
cd backend
rm -rf venv db.sqlite3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py shell < seed_data.py
python manage.py runserver 8000
```

### Start Fresh - Frontend
```bash
cd ..
rm -rf node_modules package-lock.json
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
npm run dev
```

---

**Print this page for quick reference during development!**

Last Updated: April 2026
