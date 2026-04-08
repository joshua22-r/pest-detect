# Quick Start Setup (Copy & Paste Commands)

Follow these commands in order. Copy and paste each section into your terminal.

---

## Terminal 1: Backend Setup

### Navigate to backend directory
```bash
cd backend
```

### Create Python virtual environment
```bash
python -m venv venv
```

### Activate virtual environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

### Install Python dependencies
```bash
pip install -r requirements.txt
```

### Create database migrations
```bash
python manage.py makemigrations api
```

### Apply migrations to database
```bash
python manage.py migrate
```

### Seed database with test data
```bash
python manage.py shell < seed_data.py
```

### Run Django development server
```bash
python manage.py runserver 8000
```

**Note:** Make sure your virtual environment is activated first:
- Windows: `.\venv\Scripts\Activate.ps1`
- macOS/Linux: `source venv/bin/activate`

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

**Keep this terminal running! Open a new terminal for the frontend.**

---

## Terminal 2: Frontend Setup

### Navigate to project root (from backend folder)
```bash
cd ..
```

### Create .env.local file
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

### Install Node dependencies
```bash
npm install
# or if using pnpm:
pnpm install
```

### Run Next.js development server
```bash
npm run dev
# or
pnpm dev
```

You should see:
```
▲ Next.js 16.x
  - Local:        http://localhost:3000
```

**Note:** You may see warnings about middleware or lockfiles - these are informational and don't affect functionality.

---

## Access the Application

Open your browser and navigate to:

**Frontend**: http://localhost:3000

**Admin Panel**: http://localhost:8000/admin
- Username: `josh`
- Password: `change1`

---

## Test the System

### 1. Create a new account
- Go to http://localhost:3000/auth/register
- Fill in username, email, password
- Click Register

### 2. Login
- Go to http://localhost:3000/auth/login
- Use the credentials you just created
- Click Login

### 3. Try disease detection
- Click "Detect & Analyze"
- Select "Plant" or "Livestock"
- Upload any image
- See results with disease detection and confidence scores

### 4. View scan history
- Click "History"
- See all your previous scans

### 5. Edit profile
- Click your name in top right
- Select "Profile"
- Update your information

---

## Default Admin Account

**Username:** josh
**Password:** change1

Access at: http://localhost:8000/admin

---

## Stop the Servers

When you're done testing:

**Backend (Terminal 1):**
```
Press Ctrl+C
```

**Frontend (Terminal 2):**
```
Press Ctrl+C
```

---

## Troubleshooting

### Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001
# Update .env.local:
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api" > .env.local
```

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### Virtual environment not activating
Ensure you're in the `backend` folder:
```bash
cd backend
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### "Database locked" error
```bash
rm backend/db.sqlite3
python manage.py migrate
python manage.py shell < backend/seed_data.py
```

### Network error when testing
- Ensure backend is running on Terminal 1
- Check .env.local has correct API URL
- Restart frontend dev server

---

## What's Included

✅ **Backend (Django)**
- 6 database models
- 16 API endpoints
- JWT authentication
- Mock ML detection engine
- Admin dashboard
- Image upload handling

✅ **Frontend (Next.js)**
- 7 full pages
- Authentication (login/register)
- Disease detection interface
- Scan history & filtering
- User profile management
- Admin dashboard
- Mobile responsive design

✅ **Database**
- SQLite (local development)
- Pre-seeded with diseases, plants, animals
- 7 database tables
- Ready for production migration to PostgreSQL

---

## Next Steps

1. **Explore the admin panel** - Manage diseases, users, view statistics
2. **Test all features** - Registration, login, detection, history
3. **Upload test images** - Mock ML detects diseases with realistic confidence
4. **Customize data** - Add more plants, animals, diseases via admin
5. **Production deployment** - Follow deployment guides in documentation

---

## Key Files

- **Frontend**: All in `/app`, `/components`, `/lib`
- **Backend**: All in `/backend/api/`, `/backend/config/`
- **Database**: `/backend/db.sqlite3`
- **API Client**: `/lib/api-client.ts`
- **Auth Context**: `/contexts/auth-context.tsx`

---

## Documentation

For more detailed information:
- `DJANGO_INTEGRATION.md` - Complete integration guide
- `backend/SETUP.md` - Backend details
- `README.md` - Project overview
- `backend/api/ml_detector.py` - ML detection logic

---

**You're all set! Happy testing!**
