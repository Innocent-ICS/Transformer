# Runyoro Deployment Guide

Complete guide for deploying the Runyoro application to production, including all environment variables and configuration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Post-Deployment Checklist](#post-deployment-checklist)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- [x] Supabase account and project created
- [x] Backend hosting service account (Render, Railway, Heroku, or AWS)
- [x] Frontend hosting service account (Vercel, Netlify, or AWS)
- [x] Domain name (optional but recommended)
- [x] SSL certificate (usually provided by hosting service)

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the `backend/` directory (use `.env.example` as template):

```bash
# ======================
# JWT CONFIGURATION
# ======================
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-super-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ======================
# SUPABASE DATABASE
# ======================
# Get from: https://app.supabase.com/project/_/settings/api
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-public-key
# Optional: Service role key for admin operations
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# ======================
# CORS CONFIGURATION
# ======================
# Production frontend URLs (comma-separated)
ALLOWED_ORIGINS=https://runyoro.vercel.app,https://www.yourdomain.com

# ======================
# OPTIONAL: MODEL PATHS
# ======================
# If deploying with pre-trained models
MODEL_CHECKPOINT_PATH=/app/checkpoints
VOCAB_PATH=/app/Train
```

#### Environment Variables Explained

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `JWT_SECRET_KEY` | ✅ Yes | Secret key for signing JWT tokens. **Must be random and secure.** | `a8f5f167f44f4964e6c998dee827110c` |
| `JWT_ALGORITHM` | ✅ Yes | Algorithm for JWT encoding | `HS256` |
| `JWT_EXPIRATION_HOURS` | ✅ Yes | Token validity period in hours | `24` |
| `SUPABASE_URL` | ✅ Yes | Your Supabase project URL | `https://abcdefgh.supabase.co` |
| `SUPABASE_KEY` | ✅ Yes | Supabase anon/public API key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_SERVICE_KEY` | ⚠️ Optional | Service role key for admin operations | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `ALLOWED_ORIGINS` | ✅ Yes | Comma-separated list of allowed frontend URLs | `https://app.example.com` |

> [!CAUTION]
> **Never commit `.env` files to version control!** Add `.env` to `.gitignore`.

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# ======================
# BACKEND API URL
# ======================
# Production backend URL (no trailing slash)
NEXT_PUBLIC_API_URL=https://api.runyoro.com/api

# ======================
# OPTIONAL: ANALYTICS
# ======================
NEXT_PUBLIC_GA_TRACKING_ID=G-XXXXXXXXXX
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your-analytics-id
```

#### Frontend Variables Explained

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | Full URL to your backend API (including `/api` prefix) | `https://api.runyoro.com/api` |
| `NEXT_PUBLIC_GA_TRACKING_ID` | ❌ No | Google Analytics tracking ID | `G-XXXXXXXXXX` |

> [!NOTE]
> Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Never store secrets in these variables.

---

## Database Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in:
   - **Name:** Runyoro
   - **Database Password:** (save this securely)
   - **Region:** Choose closest to your users
4. Click "Create new project" and wait for provisioning (~2 minutes)

### 2. Create Users Table

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Paste and run this SQL:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own data
CREATE POLICY "Users can read own data"
    ON users
    FOR SELECT
    USING (auth.uid() = id::text);

-- Policy: Anyone can signup (insert)
CREATE POLICY "Anyone can signup"
    ON users
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can update their own data
CREATE POLICY "Users can update own data"
    ON users
    FOR UPDATE
    USING (auth.uid() = id::text)
    WITH CHECK (auth.uid() = id::text);
```

### 3. Get API Keys

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon public** key → Use as `SUPABASE_KEY`
   - **service_role** key (optional) → Use as `SUPABASE_SERVICE_KEY`

---

## Backend Deployment

### Option 1: Deploy to Render

1. **Create Account:** Sign up at [render.com](https://render.com)

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** runyoro-backend
     - **Region:** Choose closest to your users
     - **Branch:** main
     - **Root Directory:** `backend`
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables:**
   Go to "Environment" tab and add all [backend environment variables](#backend-environment-variables)

4. **Deploy:**
   Click "Create Web Service"
   - Render will automatically deploy on every push to main branch
   - Your API will be available at: `https://runyoro-backend.onrender.com`

### Option 2: Deploy to Railway

1. **Create Account:** Sign up at [railway.app](https://railway.app)

2. **New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Service:**
   - **Root Directory:** `/backend`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables:**
   In "Variables" tab, add all [backend environment variables](#backend-environment-variables)

5. **Generate Domain:**
   Go to "Settings" → "Generate Domain"
   - Your API will be available at: `https://runyoro-backend.up.railway.app`

### Option 3: Deploy to Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create app
heroku create runyoro-backend

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set SUPABASE_URL=https://your-project.supabase.co
heroku config:set SUPABASE_KEY=your-key
heroku config:set ALLOWED_ORIGINS=https://runyoro.vercel.app

# Create Procfile in backend directory
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git subtree push --prefix backend heroku main
```

---

## Frontend Deployment

### Option 1: Deploy to Vercel (Recommended)

1. **Create Account:** Sign up at [vercel.com](https://vercel.com)

2. **Import Project:**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js

3. **Configure Settings:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)

4. **Add Environment Variables:**
   In "Settings" → "Environment Variables", add:
   ```
   NEXT_PUBLIC_API_URL=https://runyoro-backend.onrender.com/api
   ```

5. **Deploy:**
   Click "Deploy"
   - Auto-deploys on every push to main
   - Available at: `https://runyoro.vercel.app`

### Option 2: Deploy to Netlify

1. **Create Account:** Sign up at [netlify.com](https://netlify.com)

2. **New Site:**
   - Click "Add new site" → "Import an existing project"
   - Connect GitHub repository

3. **Build Settings:**
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `.next`

4. **Environment Variables:**
   Go to "Site settings" → "Environment variables"
   ```
   NEXT_PUBLIC_API_URL=https://runyoro-backend.onrender.com/api
   ```

5. **Deploy:**
   Click "Deploy site"

---

## Post-Deployment Checklist

After deploying both backend and frontend:

### 1. Test API Endpoints

```bash
# Health check
curl https://your-backend-url.com/api/health

# Signup test
curl -X POST https://your-backend-url.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456","name":"Test User"}'

# Login test
curl -X POST https://your-backend-url.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'
```

### 2. Test Frontend

- [ ] Visit your frontend URL
- [ ] Test signup flow
- [ ] Test login flow
- [ ] Test logout
- [ ] Test translation/generation features
- [ ] Test theme switching (dark/light mode)
- [ ] Check browser console for errors

### 3. Security Checklist

- [ ] HTTPS enabled on both frontend and backend
- [ ] JWT secret key is random and secure (32+ characters)
- [ ] CORS origins properly configured (only production URLs)
- [ ] Supabase RLS policies enabled
- [ ] No sensitive data in environment variables exposed to frontend
- [ ] `.env` files not committed to Git
- [ ] Database password is strong and secure

### 4. Performance Optimization

- [ ] Enable compression on backend (gzip)
- [ ] Configure CDN for frontend static assets
- [ ] Set up proper caching headers
- [ ] Monitor API response times
- [ ] Optimize model loading (if applicable)

### 5. Monitoring Setup

- [ ] Set up error tracking (Sentry, LogRocket)
- [ ] Configure uptime monitoring (UptimeRobot, Pingdom)
- [ ] Enable analytics (Google Analytics, Plausible)
- [ ] Set up log aggregation (Datadog, Papertrail)

---

## Troubleshooting

### Backend Issues

**Problem:** `Failed to connect to Supabase`
- ✅ **Solution:** Check `SUPABASE_URL` and `SUPABASE_KEY` are correct
- ✅ Verify Supabase project is active and not paused

**Problem:** `CORS error when calling API from frontend`
- ✅ **Solution:** Add frontend URL to `ALLOWED_ORIGINS` in backend `.env`
- ✅ Check CORS middleware is properly configured in `main.py`

**Problem:** `JWT token invalid`
- ✅ **Solution:** Ensure `JWT_SECRET_KEY` is the same across all backend instances
- ✅ Check token hasn't expired (default 24 hours)

### Frontend Issues

**Problem:** `Failed to fetch from API`
- ✅ **Solution:** Verify `NEXT_PUBLIC_API_URL` points to correct backend URL
- ✅ Check backend is running and accessible
- ✅ Verify CORS is properly configured

**Problem:** `Environment variables not working`
- ✅ **Solution:** Ensure variables start with `NEXT_PUBLIC_` for client-side access
- ✅ Rebuild and redeploy after changing environment variables
- ✅ Clear browser cache

### Database Issues

**Problem:** `Duplicate email error on signup`
- ✅ **Solution:** This is expected behavior - user already exists
- ✅ Use login instead or use different email

**Problem:** `Row Level Security blocks access`
- ✅ **Solution:** Review RLS policies in Supabase dashboard
- ✅ Ensure policies allow the intended operations

---

## Environment Variables Quick Reference

### Backend (.env)
```bash
JWT_SECRET_KEY=<random-32-char-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
SUPABASE_URL=<your-supabase-project-url>
SUPABASE_KEY=<your-supabase-anon-key>
ALLOWED_ORIGINS=<comma-separated-frontend-urls>
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=<backend-api-url-with-/api>
```

---

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)

---

## Need Help?

If you encounter issues not covered in this guide:

1. Check backend logs in your hosting service dashboard
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Test API endpoints directly with cURL
5. Review Supabase logs for database errors

---

**Last Updated:** 2025-11-22
**Version:** 1.0
