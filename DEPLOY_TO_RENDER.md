# 🚀 Deploy VoteWise2 to Render - Quick Guide

## Step 1: Push Your Code to GitHub

```bash
# Make sure you're in the project directory
cd /home/komradkat/Documents/Repos/VoteWise2

# Add all the new files
git add .

# Commit the changes
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin main
```

---

## Step 2: Create a Render Account

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with your **GitHub account** (recommended)
4. Authorize Render to access your GitHub repositories

---

## Step 3: Create a New Web Service

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click the **"New +"** button (top right)
3. Select **"Web Service"**

---

## Step 4: Connect Your Repository

1. **Find your repository**: Search for `VoteWise2`
2. Click **"Connect"** next to your repository
3. Render will automatically detect the `render.yaml` file

---

## Step 5: Configure Your Web Service

Render should auto-fill most settings from `render.yaml`, but verify:

### Basic Settings:
- **Name**: `votewise2` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn project_config.wsgi:application`

### Instance Type:
- **Free** (for testing) - 512MB RAM, spins down after 15 min inactivity
- **Starter** ($7/month) - 512MB RAM, always on (recommended for production)

---

## Step 6: Set Environment Variables

Click on **"Environment"** tab and add these variables:

### Required Variables:

```bash
DJANGO_SETTINGS_MODULE=project_config.settings.production
```

```bash
ALLOWED_HOSTS=your-app-name.onrender.com
```
*Replace `your-app-name` with your actual Render app name*

```bash
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
```
*Replace `your-app-name` with your actual Render app name*

### Auto-Generated (Render does this):
- `SECRET_KEY` - Click **"Generate"** button
- `DATABASE_URL` - Auto-set when you add PostgreSQL database

### Optional (for email features):
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@votewise.com
```

### Optional (for AI chatbot):
```bash
GEMINI_API_KEY=your-gemini-api-key
```

---

## Step 7: Add PostgreSQL Database

### Option A: Using render.yaml (Automatic)
If you used the `render.yaml` file, Render will automatically create a PostgreSQL database.

### Option B: Manual Setup
1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `votewise2-db`
3. **Database**: `votewise2`
4. **User**: `votewise2`
5. **Region**: Same as your web service
6. **Plan**: **Free** (for testing)
7. Click **"Create Database"**

### Link Database to Web Service:
1. Go back to your **Web Service**
2. Click **"Environment"** tab
3. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Click **"Add from Database"** → Select `votewise2-db` → Select **"Internal Database URL"**

---

## Step 8: Deploy!

1. Click **"Create Web Service"** (or **"Manual Deploy"** if already created)
2. Watch the deployment logs
3. Wait 5-10 minutes for first deployment

### What Happens During Deployment:
- ✅ Installs Python 3.12.8
- ✅ Installs all dependencies from `requirements.txt`
- ✅ Collects static files
- ✅ Runs database migrations
- ✅ Starts gunicorn server

---

## Step 9: Create Superuser (Admin Account)

After deployment succeeds:

1. Go to your **Web Service** in Render Dashboard
2. Click **"Shell"** tab (top right)
3. Run this command:

```bash
python manage.py createsuperuser
```

4. Follow the prompts to create admin account

---

## Step 10: Access Your Site

Your site will be available at:
```
https://your-app-name.onrender.com
```

Admin panel:
```
https://your-app-name.onrender.com/admin/
```

---

## 🎉 You're Live!

### Post-Deployment Checklist:
- [ ] Site loads successfully
- [ ] Admin panel accessible
- [ ] User registration works
- [ ] Login works
- [ ] Face recognition works (will be slower on CPU)
- [ ] Voting functionality works

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes** of inactivity
- First request after spin-down takes **30-60 seconds**
- **512MB RAM** (tight for TensorFlow)

### Performance:
- **Face recognition is CPU-only** (no GPU on Render)
- Expect **slower face recognition** than local development
- First-time model loading may take **30-60 seconds**

### Recommended Upgrades:
- **Starter tier** ($7/month) - Always on, better for production
- **PostgreSQL Starter** ($7/month) - More storage

---

## 🐛 Troubleshooting

### "Application failed to respond"
- Check logs in Render Dashboard → Logs tab
- Verify all environment variables are set
- Ensure `ALLOWED_HOSTS` includes your Render URL

### "Database connection error"
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL database is running

### "Out of memory"
- Upgrade to Starter tier (more RAM)
- TensorFlow + DeepFace needs ~500MB-1GB

### "Static files not loading"
- Run `python manage.py collectstatic` in Shell
- Verify `STATIC_ROOT` is set correctly

### "Face recognition very slow"
- This is normal on CPU (no GPU)
- Consider caching face embeddings
- Implement async processing with Celery

---

## 📊 Monitor Your App

### View Logs:
Render Dashboard → Your Service → **Logs** tab

### View Metrics:
Render Dashboard → Your Service → **Metrics** tab

### Shell Access:
Render Dashboard → Your Service → **Shell** tab

---

## 🔄 Updating Your App

After making code changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will **automatically redeploy** when you push to GitHub!

---

## 💰 Cost Summary

### Free Tier (Testing):
- Web Service: **Free**
- PostgreSQL: **Free**
- **Total: $0/month**

### Production Setup:
- Web Service Starter: **$7/month**
- PostgreSQL Starter: **$7/month**
- **Total: $14/month**

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Django Deployment Guide**: https://docs.djangoproject.com/en/stable/howto/deployment/

---

## ✅ Quick Checklist

Before deploying:
- [ ] Code pushed to GitHub
- [ ] `requirements.txt` updated
- [ ] `runtime.txt` exists (Python 3.12.8)
- [ ] `build.sh` exists and is executable
- [ ] `render.yaml` configured
- [ ] Production settings updated

During deployment:
- [ ] Render account created
- [ ] Repository connected
- [ ] Environment variables set
- [ ] PostgreSQL database created
- [ ] Database linked to web service

After deployment:
- [ ] Site accessible
- [ ] Superuser created
- [ ] Basic functionality tested
- [ ] Logs monitored for errors

---

**Good luck with your deployment! 🚀**
