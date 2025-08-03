# Railway Deployment Guide for Cribbage Board Collection

## 🚀 Quick Setup (5 minutes)

### Step 1: Prepare the Code
1. Upload this entire project to GitHub (create a new repository)
2. Make sure all files are committed and pushed

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your cribbage board collection repository
5. Railway will automatically detect it's a Python app and deploy!

### Step 3: Access Your App
- Railway will give you a URL like: `https://your-app-name.railway.app`
- Share this URL - accessible from any device with internet!

---

## 🔧 Technical Details

### What Railway Does Automatically:
- ✅ Detects Python app from `requirements.txt`
- ✅ Installs all dependencies
- ✅ Runs the Flask app
- ✅ Provides HTTPS URL
- ✅ Handles SSL certificates
- ✅ Auto-restarts if crashes

### Cost:
- **Free tier**: 500 hours/month (about 21 days)
- **Paid tier**: $5/month for unlimited usage
- Perfect for personal use!

### Features You Get:
- 🌐 **Custom domain support** (if you have one)
- 📱 **Mobile responsive** (works on phones/tablets)
- 🔒 **HTTPS encryption** (secure)
- 🔄 **Auto-deploys** when you update GitHub
- 📊 **Usage metrics** and logs

---

## 🛠️ Files Created for Railway:

1. **`Procfile`** - Tells Railway how to start the app
2. **`railway.json`** - Railway configuration
3. **`production.py`** - Production-optimized startup script
4. **Updated `requirements.txt`** - Added production dependencies

---

## 📱 How to Use After Deployment:

### For the Owner:
1. Bookmark the Railway URL
2. Access from any device with internet
3. Add to phone home screen for app-like experience

### For Others:
- Share the Railway URL
- Works on any device (phone, tablet, computer)
- No installation needed - just open in browser

---

## 🔄 Updating the App:
1. Make changes to your code locally
2. Commit and push to GitHub
3. Railway automatically deploys the update
4. No downtime - users see changes immediately

---

## 💡 Pro Tips:
- Railway apps "sleep" after 30 minutes of inactivity (free tier)
- First load after sleeping might take 10-20 seconds
- Paid tier ($5/month) keeps apps always running
- Database and uploaded images persist between deployments

---

Ready to deploy? Follow the steps above and you'll have a live web app in minutes!
