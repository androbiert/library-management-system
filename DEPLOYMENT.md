# Deployment Guide - Render + MongoDB Atlas

This guide will help you deploy the Library Management System to Render (web hosting) with MongoDB Atlas (cloud database).

---

## Prerequisites

- [x] GitHub account with your code pushed to a repository
- [x] MongoDB Atlas account ([sign up free](https://www.mongodb.com/cloud/atlas/register))
- [x] Render account ([sign up free](https://render.com/))

---

## Part 1: MongoDB Atlas Setup

### 1. Create MongoDB Atlas Cluster

If you haven't already created a cluster:

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Click **"Build a Database"**
3. Choose **"M0 FREE"** tier
4. Select your cloud provider and region
5. Click **"Create"**

### 2. Create Database User

1. Go to **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Set username: `androbiert_db_user`
5. Set password: `matH@02@` (or your own secure password)
6. Set role: **"Read and write to any database"**
7. Click **"Add User"**

### 3. Whitelist IP Addresses

1. Go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for Render deployment)
4. Confirm by clicking **"Add Entry"**

> ⚠️ **Security Note**: For production, you should whitelist only Render's IP addresses instead of allowing all IPs.

### 4. Get Connection String

Your current connection string:
```
mongodb+srv://androbiert_db_user:matH@02@@cluster0.epaaksy.mongodb.net/?appName=Cluster0
```

**Fix the password encoding** (special characters must be URL-encoded):
- `@` becomes `%40`

**Corrected connection string for production:**
```
mongodb+srv://androbiert_db_user:matH%4002%40@cluster0.epaaksy.mongodb.net/library_db?retryWrites=true&w=majority&appName=Cluster0
```

---

## Part 2: Prepare Your Code

### 1. Verify Files

Make sure these files exist in your project:

- ✅ `build.sh` - Render build script
- ✅ `requirements.txt` - Python dependencies (including `gunicorn`)
- ✅ `app.py` - Flask application
- ✅ `config.py` - Configuration (updated for Atlas)
- ✅ `db.py` - Database connection (updated for Atlas)

### 2. Update .gitignore

Make sure `.env` is in your `.gitignore` file:

```gitignore
.env
__pycache__/
*.pyc
.DS_Store
```

### 3. Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment with MongoDB Atlas"
git push origin main
```

---

## Part 3: Deploy to Render

### 1. Create New Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `library_system` repository

### 2. Configure Web Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `library-management-system` (or your choice) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Runtime** | `Python 3` |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` |

### 3. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add the following variables:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate a random secret key (e.g., use `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `MONGO_URI` | `mongodb+srv://androbiert_db_user:matH%4002%40@cluster0.epaaksy.mongodb.net/library_db?retryWrites=true&w=majority` |
| `GEMINI_API_KEY` | `AIzaSyB_TTTniWQQP2Q-VPvYfDoZZymTvARb8ys` |
| `FLASK_ENV` | `production` |

> 🔒 **Important**: The `MONGO_URI` must have the password URL-encoded (`%40` instead of `@`)

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Run `build.sh` to install dependencies
   - Start the app with `gunicorn`

Wait 2-5 minutes for deployment to complete.

### 5. Verify Deployment

Once deployed, you'll get a URL like: `https://library-management-system-xxxx.onrender.com`

1. Open the URL in your browser
2. You should see your Library Management System homepage
3. Try registering a new user and logging in

---

## Part 4: Initial Data Setup

Your deployed app starts with an empty database. You have two options:

### Option A: Seed Data via Script (Recommended)

If you have a `seed_db.py` script:

1. **Temporarily set MongoDB URI locally** to point to Atlas
2. Run the seed script:
   ```bash
   python seed_db.py
   ```

### Option B: Manual Setup

1. Go to your deployed app
2. Register an admin user manually
3. Add books through the admin interface

---

## Troubleshooting

### Issue: "Application Error" on Render

**Check Render Logs:**
1. Go to Render Dashboard → Your Web Service
2. Click **"Logs"** tab
3. Look for error messages

**Common fixes:**
- Verify `MONGO_URI` environment variable is correct
- Ensure password is URL-encoded
- Check that MongoDB Atlas allows connections from anywhere

### Issue: "Authentication Failed" MongoDB Error

**Fix:**
1. Verify username and password in MongoDB Atlas
2. Ensure password special characters are URL-encoded:
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`

### Issue: App works locally but not on Render

**Check:**
1. Environment variables are set in Render (not in `.env` file)
2. `gunicorn` is in `requirements.txt`
3. Build command is `bash build.sh`
4. Start command is `gunicorn app:app`

---

## Post-Deployment

### Monitor Your App

- **Render Dashboard**: View logs, metrics, and deployment status
- **MongoDB Atlas**: Monitor database usage, performance

### Auto-Deploy

Render automatically redeploys when you push to your GitHub repository's main branch.

### Custom Domain (Optional)

1. Go to your Render web service
2. Click **"Settings"** → **"Custom Domain"**
3. Follow instructions to add your domain

---

## Security Best Practices

1. ✅ Use strong, unique `SECRET_KEY` in production
2. ✅ Keep `.env` file out of version control
3. ✅ Rotate MongoDB password periodically
4. ❌ Don't commit API keys or passwords to GitHub
5. ✅ Monitor MongoDB Atlas for unusual activity

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com/
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/

---

## Summary

✅ **MongoDB Atlas** - Cloud database configured
✅ **Code Updated** - Config files ready for cloud
✅ **Render Deployment** - App deployed and running
✅ **Environment Variables** - Securely configured

Your Library Management System is now live! 🎉
