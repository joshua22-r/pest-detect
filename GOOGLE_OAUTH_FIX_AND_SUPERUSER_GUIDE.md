# Google OAuth Fix & Render Superuser Guide

## 1. Google Sign-In Fix (Removed Mock Data)

### ✅ Changes Made

**Frontend Updates:**
- Updated `app/auth/login/page.tsx` to use real Google Identity Services instead of mock tokens
- Added Google Identity Services script loading and initialization
- Updated `lib/api-client.ts` to support different token types (credential, id_token, access_token)
- Updated `contexts/auth-context.tsx` to pass token type to API client
- Added TypeScript types in `types/google.d.ts`

**Backend Updates:**
- Modified `backend/api/views.py` social_login function to handle Google Identity Services credential tokens
- Backend now accepts `credential` field for Google ID tokens

### 🔧 Setup Required

1. **Get Google Client ID:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select a project
   - Enable Google Identity API
   - Create OAuth 2.0 credentials
   - Add authorized domains (your domain + localhost for development)

2. **Environment Variables:**
   ```bash
   # Frontend (.env.local)
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-actual-google-client-id

   # Backend (Render environment variables)
   GOOGLE_CLIENT_ID=your-actual-google-client-id
   ```

3. **Authorized Origins & Redirects:**
   - Add `https://yourdomain.com` and `http://localhost:3000` to authorized origins
   - Add redirect URIs for your app

### 🧪 Testing

The Google sign-in now uses real OAuth instead of mock data. Users will see the actual Google sign-in popup and authenticate with real Google accounts.

---

## 2. Creating Superuser on Render

### Method 1: One-off Command (Recommended)

1. Go to your Render dashboard
2. Select your Django service
3. Go to "Shell" tab
4. Run this command:
   ```bash
   cd backend && python manage.py createsuperuser
   ```
   Follow the prompts to create username, email, and password.

### Method 2: Automated Script

Add this to your `render.yaml` build command:
```yaml
buildCommand: |
  pip install -r backend/requirements.txt &&
  cd backend &&
  python manage.py migrate &&
  python manage.py collectstatic --noinput &&
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell &&
  python manage.py shell < seed_data.py
```

### Method 3: Management Command

Create a custom management command:

1. Create `backend/api/management/commands/create_superuser.py`:
   ```python
   from django.core.management.base import BaseCommand
   from django.contrib.auth.models import User

   class Command(BaseCommand):
       def handle(self, *args, **options):
           if not User.objects.filter(username='admin').exists():
               User.objects.create_superuser('admin', 'admin@example.com', 'securepassword')
               self.stdout.write('Superuser created successfully')
           else:
               self.stdout.write('Superuser already exists')
   ```

2. Run in Render shell:
   ```bash
   cd backend && python manage.py create_superuser
   ```

### 🔐 Security Notes

- Change the default password immediately
- Use environment variables for sensitive data
- Consider using Render's secret management for credentials

---

## 3. Verification

### Test Google OAuth:
1. Start the development server
2. Go to login page
3. Click "Sign in with Google"
4. Should show real Google OAuth popup (not mock)

### Test Superuser:
1. Access Django admin at `/admin/`
2. Login with superuser credentials
3. Should have full admin access

---

## 4. Production Deployment

For production, ensure:
- ✅ Google Client ID is set in Render environment variables
- ✅ Authorized domains include your production domain
- ✅ HTTPS is enabled
- ✅ Superuser is created
- ✅ DEBUG=False in Django settings