# Django Backend Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Create Migrations
```bash
python manage.py makemigrations api
```

### 3. Apply Migrations
```bash
python manage.py migrate
```

### 4. Seed Database
```bash
python manage.py shell < seed_data.py
```

### 5. Run Server
```bash
python manage.py runserver 8000
```

Backend will be available at: `http://localhost:8000`

---

## API Endpoints

### Authentication
- **POST** `/api/auth/register/` - Register new user
- **POST** `/api/auth/login/` - Login and get JWT token
- **POST** `/api/auth/logout/` - Logout
- **GET** `/api/auth/user/` - Get current user info
- **POST** `/api/auth/refresh/` - Refresh JWT token

### Detection
- **POST** `/api/predict/` - Analyze plant/animal image for diseases

### User Scans
- **GET** `/api/detections/` - Get user's detection history
- **GET** `/api/detections/plant_scans/` - Get plant scans only
- **GET** `/api/detections/animal_scans/` - Get animal scans only
- **DELETE** `/api/detections/{id}/` - Delete a scan

### Species Database
- **GET** `/api/plants/` - List all plants
- **GET** `/api/animals/` - List all animals
- **GET** `/api/diseases/plant_diseases/` - Get plant diseases
- **GET** `/api/diseases/animal_diseases/` - Get animal/pest diseases

### User Profile
- **GET** `/api/profiles/my_profile/` - Get user profile
- **PUT** `/api/profiles/update_profile/` - Update profile

### Admin
- **GET** `/api/admin/users/` - List all users (admin only)
- **GET** `/api/admin/stats/` - Get system statistics

---

## Default Admin Credentials
- **Username**: admin
- **Password**: admin123

Login to admin panel at: `http://localhost:8000/admin`

---

## Project Structure
```
backend/
├── config/              # Django project settings
│   ├── settings.py     # Configuration
│   ├── urls.py         # Main URL routing
│   ├── wsgi.py         # WSGI application
│   └── asgi.py         # ASGI application
├── api/                # Main API app
│   ├── models.py       # Database models
│   ├── views.py        # API endpoints
│   ├── serializers.py  # DRF serializers
│   ├── ml_detector.py  # Mock ML engine
│   ├── permissions.py  # Custom permissions
│   ├── admin.py        # Django admin config
│   ├── urls.py         # API routing
│   └── migrations/     # Database migrations
├── manage.py           # Django management
├── requirements.txt    # Dependencies
└── db.sqlite3         # SQLite database
```

---

## Environment Variables (Optional)
Create `.env` file in backend folder:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Important Notes

1. **CORS Configuration**: Already configured to allow requests from localhost:3000 (frontend)
2. **Image Upload**: Supports up to 5MB files
3. **JWT Tokens**: 
   - Access token: 1 hour expiration
   - Refresh token: 7 days expiration
4. **Mock ML Detection**: Uses realistic confidence scores (85-98%)

---

## Testing

### Test User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Test Image Upload (requires token)
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "subject_type=plant"
```

---

## Production Deployment

### Before Deploying
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Update `ALLOWED_HOSTS`
4. Use PostgreSQL instead of SQLite
5. Set `SECURE_SSL_REDIRECT = True`
6. Update CORS origins

### Deploy with Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## Troubleshooting

**Port already in use:**
```bash
python manage.py runserver 8001
```

**Permission denied on migrations:**
```bash
chmod +x manage.py
```

**Database locked:**
```bash
rm db.sqlite3
python manage.py migrate
```

For more help, check Django docs: https://docs.djangoproject.com/
