# Deployment Errors Report - Pest Detect Backend

## Critical Issues Identified

### 1. ❌ Missing django-redis Package
**Status**: BLOCKING
**Error**: `ModuleNotFoundError: No module named 'django_redis'`
**Cause**: Package in requirements.txt but not installed in .venv
**Fix**: Install or update venv

### 2. ❌ Hardcoded Admin Credentials
**Status**: BLOCKING (Security)
**Location**: `backend/seed_data.py`
**Issue**: 
- admin / admin123 (hardcoded)
- josh / changeme@1 with real email exposed
**Cause**: Development credentials in production seed script
**Fix**: Use environment variables

### 3. ❌ SQLite3 Database for Production
**Status**: BLOCKING (Deployment)
**Issue**: Database persists to local file, not available on Render
**Location**: `backend/config/settings.py`
**Fix**: Switch to PostgreSQL connection string

### 4. ❌ Redis Cache Required but Not Available
**Status**: BLOCKING (Production)
**Issue**: Rate limiting requires Redis, might not be available on free tier
**Location**: `backend/config/settings.py` - CACHES configuration
**Fix**: Add fallback cache backend

### 5. ❌ Invalid render.yaml Configuration
**Status**: BLOCKING (Deployment)
**Issues**:
- `seed_data.py` in buildCommand won't work (not a Django management command)
- Shell redirect syntax incompatible with Render
- Region set to "oregon" instead of specific Render region
- Service names have spaces
**Fix**: Correct command syntax

### 6. ❌ Logging Files Won't Persist
**Status**: MEDIUM (Production)
**Issue**: Log files written to `backend/logs/` won't persist between deploys
**Location**: `backend/config/settings.py` - LOGGING configuration
**Fix**: Create logs directory or use fallback

### 7. ❌ Static Files Directory Missing
**Status**: MEDIUM (Deployment)
**Issue**: `STATIC_ROOT = BASE_DIR / 'staticfiles'` directory might not exist
**Fix**: Ensure directory exists during build

### 8. ❌ Missing Environment Variable Defaults
**Status**: MEDIUM (Production)
**Issue**: Stripe keys, email config, keys not set
**Location**: Multiple places in settings
**Fix**: Add proper defaults and validation

### 9. ⚠️  FRONTEND_URL Not Set for Render
**Status**: LOW (Config)
**Issue**: CSRF_TRUSTED_ORIGINS depends on frontend URL
**Location**: `backend/config/settings.py`
**Fix**: Add to render.yaml envVars

### 10. ⚠️  Procfile vs render.yaml Inconsistency
**Status**: LOW (Config)
**Issue**: Procfile for Heroku syntax, render.yaml for Render
**Note**: Both can coexist, but render.yaml takes precedence

---

## Priority Fix Order

1. **CRITICAL**: Install django-redis (required for system to start)
2. **CRITICAL**: Fix database configuration for Render (PostgreSQL)
3. **CRITICAL**: Fix seed_data credentials (security issue)
4. **CRITICAL**: Fix render.yaml syntax and commands
5. **CRITICAL**: Add cache fallback for production
6. **HIGH**: Create logs directory and fallback
7. **MEDIUM**: Set required environment variables
8. **MEDIUM**: Ensure static files directory exists

---

## Deployment Target: Render

### Render's Key Constraints:
- ❌ No persistent local file system (except /data for PostgreSQL)
- ✅ PostgreSQL available free
- ✅ Environment variables via dashboard
- ⚠️ Redis available but paid tier
- ✅ Static files via Render's static file server or S3

### Build Process on Render:
1. Install dependencies from requirements.txt
2. Run custom buildCommand
3. Start application with startCommand
4. Restart app if startup fails

---

## Files That Need Modification

1. `backend/config/settings.py` - Database, cache, logging, defaults
2. `backend/seed_data.py` - Remove hardcoded credentials
3. `render.yaml` - Fix buildCommand, add envVars
4. `backend/requirements.txt` - (already correct)
5. `Procfile` - (optional, for reference)
6. `backend/manage.py` - (check for issues)
7. `.env.example` - Create deployment guide

---

## Success Criteria

- ✅ `python manage.py check` outputs 0 issues
- ✅ Migrations can run: `python manage.py migrate`
- ✅ Static files collectable: `python manage.py collectstatic --noinput`
- ✅ Server starts: `gunicorn config.wsgi:application`
- ✅ All admin endpoints respond to requests
- ✅ Database is PostgreSQL in production
- ✅ No hardcoded credentials in code
- ✅ Logs don't cause errors if directory missing
- ✅ Rate limiting works or degrades gracefully

