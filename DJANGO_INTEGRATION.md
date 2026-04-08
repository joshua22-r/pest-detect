# Django Backend Integration Guide

## Complete Setup Instructions

This guide walks you through setting up both the Django backend and connecting it with the Next.js frontend.

---

## Backend Setup (Django)

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Create Database Migrations

```bash
python manage.py makemigrations api
```

Expected output:
```
Migrations for 'api':
  api/migrations/0001_initial.py
    - Create model Plant
    - Create model Animal
    - Create model Disease
    - Create model DetectionResult
    - Create model UserProfile
    - Create model SystemStatistics
```

### Step 4: Apply Migrations

```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, api, auth, contenttypes, sessions
Running migrations:
  Applying ... OK
  ... (multiple migrations)
```

### Step 5: Seed Database with Initial Data

```bash
python manage.py shell < seed_data.py
```

Expected output:
```
✓ Created superuser: admin / admin123
✓ Created plant: Tomato
✓ Created plant: Potato
... (more plants and animals)
✓ Created disease: Powdery Mildew
... (more diseases)

✅ Database seeding completed successfully!
```

### Step 6: Run Development Server

```bash
python manage.py runserver 8000
```

Expected output:
```
Watching for file changes with StatReloader
Quit the server with CONTROL-C.
Starting development server at http://127.0.0.1:8000/
```

**The backend is now running at: `http://localhost:8000`**

---

## Frontend Setup (Next.js)

The frontend is already configured, but here's how to ensure it connects to the backend.

### Step 1: Install Dependencies

```bash
# From the root project directory
npm install
# or
pnpm install
```

### Step 2: Set Backend URL

**Option A: Environment Variable** (Recommended for different environments)

Create a `.env.local` file in the root directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Option B: Default** (Already set in code)

The app defaults to `http://localhost:8000/api` if the environment variable is not set.

### Step 3: Run Frontend Development Server

```bash
npm run dev
# or
pnpm dev
```

Expected output:
```
  ▲ Next.js 16.x
  - Local:        http://localhost:3000
  - Environments: .env.local
```

**The frontend is now running at: `http://localhost:3000`**

---

## Testing the Integration

### Test 1: User Registration

1. Go to `http://localhost:3000/auth/register`
2. Fill in the form:
   - Username: `testuser1`
   - Email: `test1@example.com`
   - Password: `testpass123`
   - First Name: `Test`
   - Last Name: `User`
3. Click Register
4. Expected: Redirected to home page, logged in

### Test 2: User Login

1. Logout if currently logged in
2. Go to `http://localhost:3000/auth/login`
3. Fill in:
   - Username: `testuser1`
   - Password: `testpass123`
4. Click Login
5. Expected: Logged in, redirected to home

### Test 3: Admin Login

1. Go to `http://localhost:3000/auth/login`
2. Use credentials:
   - Username: `admin`
   - Password: `admin123`
3. Expected: Logged in as admin with admin dashboard access

### Test 4: Disease Detection

1. Login with any user
2. Go to `/predict`
3. Select "Plant" or "Livestock"
4. Upload an image (any image file works due to mock ML)
5. Expected: Results show disease detection with confidence score

### Test 5: Scan History

1. Login with a user
2. Go to `/history`
3. Expected: See all your previous scans with filter options

### Test 6: API Direct Testing

Test backend API directly with curl:

**Register User:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "password123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123"
  }'
```

Save the `access` token from response, then use for authenticated endpoints:

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Troubleshooting

### Port 8000 Already in Use

```bash
# Use a different port
python manage.py runserver 8001
```

Then update `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

### Port 3000 Already in Use

```bash
npm run dev -- -p 3001
```

### CORS Error in Browser

If you see CORS errors, the backend CORS configuration might need updating.

Edit `backend/config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',  # Add if using port 3001
]
```

Then restart the Django server.

### Network Error - Backend Not Found

Error message: "Network error. Make sure the backend is running."

Solution:
1. Check backend is running: `python manage.py runserver`
2. Verify `NEXT_PUBLIC_API_URL` is correct in `.env.local`
3. Restart frontend dev server

### Invalid Token / Session Expired

- Clear browser storage: Dev Tools → Application → Storage → Clear All
- Logout and login again
- Tokens expire after 1 hour by default

### Database Locked

If you get "database is locked" error:

```bash
# Delete database and recreate
rm backend/db.sqlite3
python manage.py migrate
python manage.py shell < backend/seed_data.py
```

---

## API Endpoints Reference

### Authentication
- **POST** `/api/auth/register/` - Register new user
- **POST** `/api/auth/login/` - Login and get JWT token
- **POST** `/api/auth/logout/` - Logout
- **GET** `/api/auth/user/` - Get current user info
- **POST** `/api/auth/refresh/` - Refresh access token

### Detection
- **POST** `/api/predict/` - Analyze image for diseases

Request:
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@image.jpg" \
  -F "subject_type=plant"
```

Response:
```json
{
  "id": "uuid",
  "image": "url/to/image",
  "subject_type": "plant",
  "disease_name": "Powdery Mildew",
  "confidence": 92.5,
  "severity": "medium",
  "treatment": "Apply fungicide...",
  "prevention": "Maintain spacing...",
  "created_at": "2026-04-06T..."
}
```

### Scan History
- **GET** `/api/detections/` - Get all user detections
- **GET** `/api/detections/plant_scans/` - Get plant scans only
- **GET** `/api/detections/animal_scans/` - Get animal scans only
- **GET** `/api/detections/{id}/` - Get specific detection
- **DELETE** `/api/detections/{id}/` - Delete a detection

### User Profile
- **GET** `/api/profiles/my_profile/` - Get user profile
- **PATCH** `/api/profiles/update_profile/` - Update profile

### Statistics
- **GET** `/api/statistics/stats/` - Get system statistics

### Admin
- **GET** `/api/admin/users/` - List all users (admin only)
- **GET** `/api/admin/stats/` - Get admin stats

### Diseases
- **GET** `/api/diseases/` - Get all diseases
- **GET** `/api/diseases/plant_diseases/` - Get plant diseases
- **GET** `/api/diseases/animal_diseases/` - Get animal diseases

---

## Environment Variables Summary

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Backend (optional - backend/config/settings.py)
- `DEBUG=True` - Enable debug mode
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

---

## How the Integration Works

1. **User Registration/Login**
   - Frontend sends credentials to backend `/auth/register/` or `/auth/login/`
   - Backend validates and returns JWT tokens (access & refresh)
   - Frontend stores tokens in localStorage
   - Tokens are automatically added to all subsequent requests

2. **Image Upload & Detection**
   - User selects/captures image on frontend
   - Frontend sends FormData with image and subject_type to `/predict/`
   - Backend runs mock ML detection
   - Backend saves result to database
   - Frontend displays results with treatment/prevention info

3. **Data Persistence**
   - All user scans, profiles, and detections stored in SQLite database
   - History automatically synced with backend
   - User can view past scans anytime

4. **Token Management**
   - Access tokens expire after 1 hour
   - Refresh tokens valid for 7 days
   - Frontend automatically refreshes tokens when expired
   - Logout clears tokens from both storage and backend

---

## Next Steps

1. **Test thoroughly** - Use all features and report any issues
2. **Customize** - Modify diseases, plants, animals in admin panel
3. **Secure** - Change SECRET_KEY before production
4. **Deploy** - Follow production deployment guide

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review error messages in console (browser Dev Tools)
3. Check Django server console for backend errors
4. Ensure both servers are running on correct ports

Happy testing!
