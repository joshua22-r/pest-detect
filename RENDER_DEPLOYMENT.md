# Render Deployment Guide for BioGuard-AI

This guide will help you deploy your BioGuard-AI application on Render.com with both frontend and backend.

## Prerequisites

- GitHub account with your repo pushed
- Render.com account (free tier available)
- Environment variables configured

## Step 1: Push Updates to GitHub

Run these commands to push the latest deployment configuration:

```bash
cd "C:\Users\joshu\Desktop\pest detect"
git add .
git commit -m "Add render deployment configuration"
git push origin main
```

## Step 2: Create Backend Service on Render

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in the configuration:
   - **Name**: `bioguard-backend`
   - **Environment**: Python 3
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt && cd backend && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```
     cd backend && gunicorn config.wsgi:application
     ```
   - **Plan**: Free

5. Add Environment Variables:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Generate a secure key at [djecrety.ir](https://djecrety.ir)
   - `ALLOWED_HOSTS`: `yourdomain.onrender.com,localhost,127.0.0.1`
   - `CORS_ALLOWED_ORIGINS`: `https://yourdomain-frontend.onrender.com,http://localhost:3000`
   - `PYTHON_VERSION`: `3.10`

6. Click **"Create Web Service"**

## Step 3: Create Frontend Service on Render

1. Click **"New +"** → **"Web Service"** again
2. Connect your GitHub repository again
3. Fill in the configuration:
   - **Name**: `bioguard-frontend`
   - **Environment**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free

4. Add Environment Variables:
   - `NODE_ENV`: `production`
   - `NEXT_PUBLIC_API_URL`: `https://yourdomain-backend.onrender.com` (use actual backend domain from Step 2)

5. Click **"Create Web Service"**

## Step 4: Update Django CORS Settings

After both services are created, you'll have:
- Backend URL: `https://yourdomain-backend.onrender.com`
- Frontend URL: `https://yourdomain-frontend.onrender.com`

Update your backend environment variables with the correct frontend URL.

## Step 5: Initialize Database

The migrations will run automatically during the build. If you need to create a superuser:

1. Go to your backend service on Render
2. Click **"Shell"**
3. Run: `python backend/manage.py createsuperuser`

## Important Notes

- **Free Tier**: Services spin down after 15 minutes of inactivity
- **Static Files**: WhiteNoise is configured to serve Django static files
- **CORS**: Make sure frontend and backend URLs match in environment variables
- **Database**: Currently using SQLite; for production scale, consider PostgreSQL
- **Media Files**: SQLite-stored files may not persist on free tier

## Troubleshooting

### Backend won't start
- Check build logs in Render dashboard
- Verify `SECRET_KEY` is set
- Ensure all migrations ran successfully

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify backend CORS settings include frontend URL
- Check browser console for CORS errors

### Static files not loading
- Run collectstatic manually in Render Shell: `python backend/manage.py collectstatic --noinput`
- Clear browser cache

## Next Steps

- Set up custom domain in Render
- Monitor application performance
- Set up error alerts
- Consider upgrading to paid tier for production use
