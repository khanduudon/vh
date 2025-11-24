# Quick Start Guide

Get your ClassPlus Batch File Retrieval Bot running in under 10 minutes!

## Prerequisites Checklist

- [ ] Telegram account
- [ ] GitHub account  
- [ ] Render.com account (free)
- [ ] MongoDB Atlas account (free)

---

## Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send: `/newbot`
3. Choose a name: `My ClassPlus Bot`
4. Choose username: `myclassplus_bot` (must end in 'bot')
5. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

✅ **Done!** Keep this token safe.

---

## Step 2: Setup MongoDB Atlas (3 minutes)

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up / Log in
3. Click **"Build a Database"** → Select **"Free"** (M0)
4. Choose region → Click **"Create Cluster"**
5. **Database Access**:
   - Add user with username/password
   - Save credentials!
6. **Network Access**:
   - Add IP: `0.0.0.0/0` (allow all)
7. **Get connection string**:
   - Click **"Connect"** → **"Connect your application"**
   - Copy the connection string
   - Replace `<password>` with your password
   - Replace `<dbname>` with `classplus_extractor`

✅ **Done!** Your connection string looks like:
```
mongodb+srv://user:pass@cluster.mongodb.net/classplus_extractor?retryWrites=true&w=majority
```

---

## Step 3: Push to GitHub (2 minutes)

### Option A: Using Git Command Line

```bash
cd "c:\Users\aman2\Downloads\Telegram Desktop\Bot\Org to TXT\Extractor"

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/classplus-bot.git
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Desktop

1. Download [GitHub Desktop](https://desktop.github.com/)
2. Open the folder in GitHub Desktop
3. Create repository
4. Publish to GitHub

✅ **Done!** Code is on GitHub.

---

## Step 4: Deploy to Render.com (3 minutes)

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your repository
5. Configure:
   - **Name**: `classplus-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot.py`
   - **Instance Type**: Free

6. **Add Environment Variables**:
   
   Click "Advanced" → Add:
   
   | Key | Value |
   |-----|-------|
   | `BOT_TOKEN` | Your bot token from Step 1 |
   | `MONGODB_URI` | Your connection string from Step 2 |
   | `DATABASE_NAME` | `classplus_extractor` |
   | `CACHE_DIR` | `/tmp/cache/batch_files` |

7. Click **"Create Web Service"**

✅ **Done!** Bot is deploying (takes 2-3 minutes).

---

## Step 5: Test Your Bot! (1 minute)

1. Open Telegram
2. Search for your bot username
3. Send: `/start`
4. You should see the welcome message!
5. Try: `/getbatches`
6. Enter an org code

✅ **Success!** Your bot is live! 🎉

---

## Troubleshooting

### Bot not responding?

1. Check Render logs for errors
2. Verify `BOT_TOKEN` is correct
3. Make sure service is running

### MongoDB connection failed?

1. Check connection string format
2. Verify password is URL-encoded
3. Confirm IP whitelist includes `0.0.0.0/0`

### Files not downloading?

1. Check org code is valid
2. Verify MongoDB has space
3. Check file size (must be < 50 MB for Telegram)

---

## Next Steps

- 📖 Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- 📖 Check [README.md](README.md) for full documentation
- 🔧 Customize bot messages in `telegram_bot.py`
- 📊 Monitor usage in Render dashboard

---

## Support

Need help? Check:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- [README.md](README.md) - Complete documentation
- Render logs - For error messages
- MongoDB Atlas logs - For database issues

---

**Congratulations! Your bot is now live and ready to use! 🚀**
