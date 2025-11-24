# FINAL DEPLOYMENT CONFIGURATION
# Your bot is ready to deploy with these credentials

## Your Credentials

### Telegram Bot
- **Bot Token**: `8508365196:AAFQF5mD5RFEq1YBYxztSgPIjt0clxUhMzE`

### MongoDB Atlas (NEW - Updated)
- **Connection String**: `mongodb+srv://nk9582235_db_user:TVM1VuULifESdFb9@cluster0.gsewrqr.mongodb.net/?appName=Cluster0`
- **Database Name**: `classplus_extractor`
- **Password**: `TVM1VuULifESdFb9`

---

## 🚀 Deploy to Render.com NOW

### Step 1: Push to GitHub (2 minutes)

```bash
cd "c:\Users\aman2\Downloads\Telegram Desktop\Bot\Org to TXT\Extractor"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "ClassPlus Batch Bot - Ready for deployment"

# Create repository on GitHub, then push
git remote add origin https://github.com/YOUR_USERNAME/classplus-batch-bot.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render.com (3 minutes)

1. Go to **[render.com](https://render.com)** and sign in with GitHub

2. Click **"New +"** → **"Web Service"**

3. Connect your GitHub repository

4. Configure:
   - **Name**: `classplus-batch-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot.py`
   - **Instance Type**: Free

5. **Add Environment Variables** (Click "Advanced"):

   | Key | Value |
   |-----|-------|
   | `BOT_TOKEN` | `8508365196:AAFQF5mD5RFEq1YBYxztSgPIjt0clxUhMzE` |
   | `MONGODB_URI` | `mongodb+srv://nk9582235_db_user:TVM1VuULifESdFb9@cluster0.gsewrqr.mongodb.net/?appName=Cluster0` |
   | `DATABASE_NAME` | `classplus_extractor` |
   | `CACHE_DIR` | `/tmp/cache/batch_files` |
   | `LOG_LEVEL` | `INFO` |
   | `CLASSPLUS_BASE_URL` | `https://api.classplusapp.com` |
   | `API_TIMEOUT` | `30` |
   | `MAX_RETRIES` | `3` |
   | `CACHE_ENABLED` | `True` |

6. Click **"Create Web Service"**

7. Wait 2-3 minutes for deployment

### Step 3: Test Your Bot!

1. Open Telegram
2. Search for your bot (the username you set with @BotFather)
3. Send: `/start`
4. You should see the welcome message!
5. Try: `/getbatches` and enter an org code

---

## 🧪 Test Locally First (Optional)

If you want to test before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script (creates .env with your credentials)
python setup_env.py
# When prompted, enter: 8547108711:AAF-cjQuyfEHZ_FZDIwz0Qj8Sf2bZ6AAG50

# Run the bot
python telegram_bot.py
```

Then test in Telegram!

---

## ✅ Pre-Deployment Checklist

- [x] MongoDB Atlas configured
- [x] Bot token obtained
- [x] Code ready
- [x] Dependencies listed
- [x] Deployment config created
- [ ] Code pushed to GitHub
- [ ] Deployed on Render.com
- [ ] Tested in Telegram

---

## 📱 Bot Commands

Once deployed, your bot supports:

- `/start` - Welcome message
- `/help` - Help and instructions
- `/getbatches` - Retrieve batch files by org code
- `/cancel` - Cancel current operation

---

## 🔒 Security Notes

**IMPORTANT**: 
- Your credentials are configured for deployment
- Never share your bot token publicly
- The `.env` file (if created) is in `.gitignore`
- MongoDB password is in the connection string

---

## 🎯 What Happens After Deployment

1. **Bot goes live** on Render.com
2. **Auto-deploys** when you push to GitHub
3. **Connects to MongoDB** Atlas automatically
4. **Users can interact** via Telegram
5. **Files are cached** for faster retrieval
6. **Logs available** in Render dashboard

---

## 📊 Monitoring

After deployment:
- **Render Dashboard**: Check logs and status
- **MongoDB Atlas**: Monitor database usage
- **Telegram**: Test bot functionality

---

## 🆘 If Something Goes Wrong

### Bot not responding?
1. Check Render logs
2. Verify environment variables
3. Ensure service is running

### MongoDB errors?
1. Check connection string
2. Verify network access (0.0.0.0/0)
3. Confirm user permissions

### Files not downloading?
1. Verify org code is valid
2. Check file size < 50 MB
3. Review bot logs

---

## 🚀 You're Ready!

Everything is configured. Just:
1. Push to GitHub
2. Deploy on Render.com (use the environment variables above)
3. Test in Telegram!

**Your bot will be live in under 5 minutes! 🎉**
