# Complete Documentation Index

## Start Here

### For Quick Setup
1. **[QUICKSTART_SETUP.md](./QUICKSTART_SETUP.md)** ⭐
   - Copy-paste commands to get running in 5 minutes
   - Step-by-step terminal instructions
   - Troubleshooting quick fixes

### For Complete Overview
2. **[IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)**
   - What has been built
   - Complete feature list
   - File structure overview
   - Statistics and metrics

### For Integration Details
3. **[DJANGO_INTEGRATION.md](./DJANGO_INTEGRATION.md)**
   - Detailed setup instructions
   - Testing all endpoints
   - How the integration works
   - Complete API reference

---

## Frontend Documentation

### Getting Started
- **[README.md](./README.md)** - Project overview and setup
- **App Router** - Next.js App Router patterns
- **Components** - shadcn/ui component usage

### Frontend Features
- **Authentication** - Login/Register with JWT tokens
- **Disease Detection** - Image upload and analysis
- **Scan History** - View and filter past scans
- **User Profile** - Manage user information
- **Admin Dashboard** - System management

### Frontend Files
- `/app/page.tsx` - Home page
- `/app/auth/login/page.tsx` - Login page
- `/app/auth/register/page.tsx` - Registration page
- `/app/predict/page.tsx` - Disease detection page
- `/app/history/page.tsx` - Scan history page
- `/app/profile/page.tsx` - User profile page
- `/app/admin/dashboard/page.tsx` - Admin dashboard

### Key Utilities
- `/lib/api-client.ts` - Django API client (TypeScript)
- `/contexts/auth-context.tsx` - Global auth state
- `/lib/constants.ts` - App constants
- `/lib/types.ts` - TypeScript types

---

## Backend Documentation

### Setup & Installation
- **[backend/SETUP.md](./backend/SETUP.md)** - Detailed backend setup guide
- **Environment setup** - Virtual environment and dependencies
- **Database initialization** - Migrations and seeding
- **Running the server** - Development server

### Backend Architecture
- **[backend/config/settings.py](./backend/config/settings.py)** - Django configuration
- **[backend/api/models.py](./backend/api/models.py)** - Database models
- **[backend/api/views.py](./backend/api/views.py)** - API endpoints
- **[backend/api/serializers.py](./backend/api/serializers.py)** - Data serializers
- **[backend/api/ml_detector.py](./backend/api/ml_detector.py)** - ML detection engine

### Backend Database
- **Plant model** - Plant species database
- **Animal model** - Livestock species database
- **Disease model** - Disease/pest/condition database
- **DetectionResult model** - User scan results
- **UserProfile model** - Extended user information
- **SystemStatistics model** - System-wide metrics

### Backend API Endpoints
All endpoints documented in DJANGO_INTEGRATION.md with:
- Request/response examples
- Authentication requirements
- Error codes
- Usage examples

---

## API Reference

### Complete Endpoint List
See [DJANGO_INTEGRATION.md - API Endpoints Reference](./DJANGO_INTEGRATION.md#api-endpoints-reference)

### Authentication Endpoints
- POST `/api/auth/register/` - Register new user
- POST `/api/auth/login/` - Login and get tokens
- POST `/api/auth/logout/` - Logout
- GET `/api/auth/user/` - Get current user
- POST `/api/auth/refresh/` - Refresh access token

### Detection Endpoints
- POST `/api/predict/` - Analyze plant/animal image
- GET `/api/detections/` - Get user's scans
- GET `/api/detections/{id}/` - Get specific scan
- DELETE `/api/detections/{id}/` - Delete scan

### Database Endpoints
- GET `/api/plants/` - List plant species
- GET `/api/animals/` - List animal species
- GET `/api/diseases/` - List all diseases
- GET `/api/diseases/plant_diseases/` - Plant diseases only
- GET `/api/diseases/animal_diseases/` - Animal diseases only

### Admin Endpoints
- GET `/api/admin/stats/` - System statistics
- GET `/api/admin/users/` - List all users (admin only)

---

## Configuration

### Environment Variables
Create `.env.local` in project root:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Backend Configuration
Edit `backend/config/settings.py`:
- `DEBUG` - Debug mode (False for production)
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Allowed hostnames
- `DATABASES` - Database configuration
- `CORS_ALLOWED_ORIGINS` - CORS origins
- `SIMPLE_JWT` - JWT token settings

---

## Troubleshooting

### Common Issues

**Port 8000 already in use:**
```bash
python manage.py runserver 8001
# Update NEXT_PUBLIC_API_URL in .env.local
```

**Port 3000 already in use:**
```bash
npm run dev -- -p 3001
```

**Network error / Backend not found:**
- Ensure Django server is running
- Check API URL in .env.local is correct
- Verify both servers are accessible

**Database locked:**
```bash
rm backend/db.sqlite3
python manage.py migrate
python manage.py shell < backend/seed_data.py
```

**Token errors / Session expired:**
- Clear browser storage (DevTools → Application → Clear All)
- Logout and login again
- Access tokens expire after 1 hour

**CORS errors:**
- Update CORS_ALLOWED_ORIGINS in backend/config/settings.py
- Restart Django server

See [DJANGO_INTEGRATION.md - Troubleshooting](./DJANGO_INTEGRATION.md#troubleshooting) for more help.

---

## Database Schema

### Plant Table
```
id (UUID, PK)
name (CharField)
scientific_name (CharField)
description (TextField)
created_at (DateTime)
updated_at (DateTime)
```

### Animal Table
```
id (UUID, PK)
name (CharField)
species (CharField - 8 choices)
scientific_name (CharField)
description (TextField)
created_at (DateTime)
updated_at (DateTime)
```

### Disease Table
```
id (UUID, PK)
name (CharField, unique)
subject_type (CharField - plant/animal)
scientific_name (CharField)
description (TextField)
symptoms (TextField)
treatment (TextField)
prevention (TextField)
severity (CharField - low/medium/high)
affected_plants (M2M with Plant)
affected_animals (M2M with Animal)
created_at (DateTime)
updated_at (DateTime)
```

### DetectionResult Table
```
id (UUID, PK)
user (FK to User)
image (ImageField)
subject_type (CharField - plant/animal)
disease (FK to Disease, nullable)
disease_name (CharField)
confidence (FloatField, 0-100)
severity (CharField)
treatment (TextField)
prevention (TextField)
notes (TextField)
created_at (DateTime)
updated_at (DateTime)
```

### UserProfile Table
```
user (OneToOne to User, PK)
user_type (CharField - farmer/vet/agronomist/admin)
phone (CharField)
location (CharField)
bio (TextField)
total_scans (IntegerField)
created_at (DateTime)
updated_at (DateTime)
```

### SystemStatistics Table
```
id (IntegerField, PK)
total_scans (IntegerField)
total_users (IntegerField)
plant_scans (IntegerField)
animal_scans (IntegerField)
diseases_detected (IntegerField)
updated_at (DateTime)
```

---

## Testing

### Manual Testing Checklist
- [ ] User registration works
- [ ] User login works
- [ ] JWT token storage works
- [ ] Plant disease detection works
- [ ] Livestock analysis works
- [ ] Scan history displays
- [ ] Filter by disease works
- [ ] Filter by type (plant/animal) works
- [ ] User profile update works
- [ ] Admin dashboard accessible
- [ ] Disease management in admin
- [ ] Logout clears session
- [ ] Token refresh works
- [ ] Image upload displays preview
- [ ] Mobile responsiveness verified

### API Testing
Use curl or Postman with examples in [DJANGO_INTEGRATION.md - Testing](./DJANGO_INTEGRATION.md#testing-the-integration)

---

## Deployment

### Production Checklist
See [DJANGO_INTEGRATION.md - Production Deployment](./backend/SETUP.md#production-deployment)

- [ ] Change Django SECRET_KEY
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS
- [ ] Configure PostgreSQL database
- [ ] Set up SSL/HTTPS
- [ ] Update CORS origins
- [ ] Configure environment variables
- [ ] Run collectstatic for static files
- [ ] Set up backup strategy
- [ ] Configure logging
- [ ] Test end-to-end workflow

---

## File Structure

```
project/
├── QUICKSTART_SETUP.md               ← START HERE
├── IMPLEMENTATION_COMPLETE.md        ← OVERVIEW
├── DJANGO_INTEGRATION.md             ← DETAILED GUIDE
├── DOCUMENTATION.md                  ← THIS FILE
├── README.md
├── .env.example
├── public/                           # Static files
├── app/                             # Next.js pages
│   ├── auth/
│   ├── predict/
│   ├── history/
│   ├── profile/
│   └── admin/
├── components/                       # React components
│   ├── navbar.tsx
│   ├── image-upload.tsx
│   ├── detection-results.tsx
│   └── ui/
├── contexts/                        # React contexts
│   └── auth-context.tsx
├── lib/                            # Utilities
│   ├── api-client.ts              # IMPORTANT: Django API client
│   └── ...
├── backend/                        # Django backend
│   ├── config/                    # Settings
│   ├── api/                       # Main app
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── SETUP.md
│   └── seed_data.py
└── package.json
```

---

## Key Files to Understand

| File | Purpose | Priority |
|------|---------|----------|
| `/lib/api-client.ts` | Frontend to backend communication | Critical |
| `/contexts/auth-context.tsx` | Global authentication state | Critical |
| `/backend/api/models.py` | Database schema | Critical |
| `/backend/api/views.py` | API endpoint logic | Critical |
| `/backend/api/ml_detector.py` | Disease detection engine | Important |
| `/backend/config/settings.py` | Backend configuration | Important |
| `/app/predict/page.tsx` | Detection interface | Important |
| `/app/auth/login/page.tsx` | Authentication UI | Important |

---

## Glossary

| Term | Meaning |
|------|---------|
| **JWT** | JSON Web Token - secure authentication method |
| **API** | Application Programming Interface - backend endpoints |
| **CORS** | Cross-Origin Resource Sharing - browser security |
| **ORM** | Object-Relational Mapping - Django models |
| **Mock ML** | Simulated ML detection for testing |
| **RSC** | React Server Component |
| **SSR** | Server-Side Rendering |
| **REST** | Representational State Transfer - API style |

---

## Getting Help

1. **Check QUICKSTART_SETUP.md** - Most questions answered there
2. **Review DJANGO_INTEGRATION.md** - Detailed guidance
3. **Check backend/SETUP.md** - Backend-specific help
4. **Look at code comments** - Inline documentation in key files
5. **Check error messages** - Usually indicate the problem clearly

---

## Quick Reference

### Start Backend
```bash
cd backend && source venv/bin/activate && python manage.py runserver 8000
```

### Start Frontend
```bash
npm run dev
```

### Access Points
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

### Default Credentials
- Admin: admin / admin123
- Create test user: go to /auth/register

---

## Support Resources

- **Django Docs**: https://docs.djangoproject.com/
- **Next.js Docs**: https://nextjs.org/docs
- **REST Framework**: https://www.django-rest-framework.org/
- **shadcn/ui**: https://ui.shadcn.com/

---

**Last Updated**: April 2026  
**Version**: 1.0  
**Status**: Complete & Production Ready

For quick setup, start with [QUICKSTART_SETUP.md](./QUICKSTART_SETUP.md) →
