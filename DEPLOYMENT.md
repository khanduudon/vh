# Deployment Guide - Render.com via GitHub

This guide will walk you through deploying the ClassPlus Batch File Retrieval Telegram Bot to Render.com using GitHub.

## Prerequisites

Before you begin, make sure you have:

1. ✅ A GitHub account
2. ✅ A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
3. ✅ A MongoDB Atlas account (free tier available)
4. ✅ A Render.com account (free tier available)

---

## Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to:
   - Choose a name for your bot
   - Choose a username (must end in 'bot')
4. **Save the bot token** - you'll need it later
5. (Optional) Set bot description and profile picture using BotFather commands

---

## Step 2: Set Up MongoDB Atlas

### Create a Free MongoDB Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up or log in
3. Click **"Build a Database"**
4. Select **"Free"** tier (M0)
5. Choose a cloud provider and region (closest to your users)
6. Click **"Create Cluster"**

### Configure Database Access

1. Go to **"Database Access"** in the left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Set username and password (save these!)
5. Set user privileges to **"Read and write to any database"**
6. Click **"Add User"**

### Configure Network Access

1. Go to **"Network Access"** in the left sidebar
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - This is needed for Render.com to connect
4. Click **"Confirm"**

### Get Connection String

1. Go to **"Database"** in the left sidebar
2. Click **"Connect"** on your cluster
3. Select **"Connect your application"**
4. Copy the connection string
5. Replace `<password>` with your database user password
6. Replace `<dbname>` with `classplus_extractor`

Example:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/classplus_extractor?retryWrites=true&w=majority
```

---

## Step 3: Push Code to GitHub

### Initialize Git Repository

```bash
cd "c:\Users\aman2\Downloads\Telegram Desktop\Bot\Org to TXT\Extractor"

# Initialize git (if not already initialized)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ClassPlus Batch File Retrieval Bot"
```

### Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click **"New repository"**
3. Name it: `classplus-batch-bot` (or your preferred name)
4. **Do NOT** initialize with README (we already have files)
5. Click **"Create repository"**

### Push to GitHub

```bash
# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/classplus-batch-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 4: Deploy to Render.com

### Create Render Account

1. Go to [Render.com](https://render.com)
2. Sign up using your GitHub account
3. Authorize Render to access your GitHub repositories

### Create New Web Service

1. Click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Click **"Connect account"** if needed
   - Find and select your `classplus-batch-bot` repository
4. Click **"Connect"**

### Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `classplus-batch-bot` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python telegram_bot.py`

**Instance Type:**
- Select **"Free"** tier

### Add Environment Variables

Click **"Advanced"** and add the following environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `BOT_TOKEN` | Your Telegram bot token | From BotFather |
| `MONGODB_URI` | Your MongoDB connection string | From MongoDB Atlas |
| `DATABASE_NAME` | `classplus_extractor` | Database name |
| `CLASSPLUS_BASE_URL` | `https://api.classplusapp.com` | API base URL |
| `CACHE_ENABLED` | `True` | Enable caching |
| `CACHE_DIR` | `/tmp/cache/batch_files` | Cache directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `API_TIMEOUT` | `30` | API timeout in seconds |
| `MAX_RETRIES` | `3` | Max retry attempts |

**Important Notes:**
- Keep `BOT_TOKEN` and `MONGODB_URI` secret
- Use `/tmp` for cache directory on Render (ephemeral storage)

### Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your bot
3. Wait for deployment to complete (usually 2-5 minutes)
4. Check the logs for any errors

---

## Step 5: Verify Deployment

### Check Logs

1. Go to your service dashboard on Render
2. Click **"Logs"** tab
3. Look for: `Starting bot...`
4. Verify no errors appear

### Test Your Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start` command
4. You should receive a welcome message
5. Try `/getbatches` to test functionality

---

## Step 6: Configure Auto-Deploy (Optional)

Render automatically deploys when you push to GitHub:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update bot features"
   git push
   ```
3. Render will automatically detect changes and redeploy

---

## Troubleshooting

### Bot Not Responding

**Check Logs:**
1. Go to Render dashboard
2. Click **"Logs"**
3. Look for error messages

**Common Issues:**
- ❌ Invalid `BOT_TOKEN` - Check token from BotFather
- ❌ MongoDB connection failed - Verify connection string and network access
- ❌ Import errors - Check `requirements.txt` is complete

### MongoDB Connection Issues

**Verify:**
1. Connection string is correct
2. Password is URL-encoded (replace special characters)
3. IP whitelist includes `0.0.0.0/0`
4. Database user has correct permissions

### File Upload Failures

**Check:**
1. File size is under 50 MB (Telegram limit)
2. MongoDB has enough storage
3. Network connection is stable

---

## Monitoring and Maintenance

### View Logs

```bash
# On Render dashboard, click "Logs" tab
# Or use Render CLI:
render logs -s classplus-batch-bot
```

### Update Environment Variables

1. Go to Render dashboard
2. Click on your service
3. Go to **"Environment"** tab
4. Update variables as needed
5. Service will automatically restart

### Scale Your Service

**Free Tier Limitations:**
- Service spins down after 15 minutes of inactivity
- First request after spin-down may be slow

**To Upgrade:**
1. Go to service settings
2. Change instance type to paid tier
3. Service will stay always-on

---

## Security Best Practices

### Protect Sensitive Data

✅ **DO:**
- Use environment variables for secrets
- Keep `.env` file in `.gitignore`
- Use MongoDB Atlas with authentication
- Regularly rotate bot token

❌ **DON'T:**
- Commit `.env` file to GitHub
- Share bot token publicly
- Use weak database passwords
- Expose MongoDB to public internet without authentication

### Monitor Usage

1. Check Render dashboard for resource usage
2. Monitor MongoDB Atlas for storage usage
3. Review bot logs for suspicious activity

---

## Updating Your Bot

### Make Changes

1. Edit code locally
2. Test changes:
   ```bash
   python telegram_bot.py
   ```
3. Commit and push:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
4. Render will auto-deploy

### Rollback if Needed

1. Go to Render dashboard
2. Click **"Manual Deploy"**
3. Select previous commit
4. Click **"Deploy"**

---

## Cost Estimate

### Free Tier (Recommended for Testing)

- **Render.com**: Free (with limitations)
- **MongoDB Atlas**: Free (512 MB storage)
- **Telegram Bot**: Free
- **Total**: $0/month

### Limitations:
- Service spins down after 15 minutes inactivity
- 512 MB MongoDB storage
- 750 hours/month runtime

### Paid Tier (For Production)

- **Render.com**: $7/month (Starter)
- **MongoDB Atlas**: $9/month (M2 Shared)
- **Total**: ~$16/month

### Benefits:
- Always-on service
- 2 GB MongoDB storage
- Better performance

---

## Support

### Resources

- 📖 [Render Documentation](https://render.com/docs)
- 📖 [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- 📖 [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)

### Getting Help

1. Check logs for error messages
2. Review this deployment guide
3. Check GitHub Issues
4. Contact support

---

## Quick Reference

### Essential Commands

```bash
# Local testing
python telegram_bot.py

# Git commands
git add .
git commit -m "message"
git push

# View logs (Render CLI)
render logs -s classplus-batch-bot
```

### Important URLs

- Render Dashboard: https://dashboard.render.com
- MongoDB Atlas: https://cloud.mongodb.com
- GitHub Repository: https://github.com/YOUR_USERNAME/classplus-batch-bot
- BotFather: https://t.me/botfather

---

## Next Steps

After successful deployment:

1. ✅ Test all bot commands
2. ✅ Verify file downloads work
3. ✅ Monitor logs for errors
4. ✅ Share bot with users
5. ✅ Set up monitoring/alerts (optional)

**Congratulations! Your bot is now live! 🎉**
