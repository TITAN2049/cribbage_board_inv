@echo off
title Deploy to Railway - Setup Guide

cls
echo.
echo  ████████████████████████████████████████████████████████████████████████████
echo  █                                                                          █
echo  █                    Railway Deployment Helper                            █  
echo  █                                                                          █
echo  ████████████████████████████████████████████████████████████████████████████
echo.
echo  This will guide you through deploying to Railway for multi-device access!
echo.
echo  📋 WHAT YOU NEED:
echo     1. GitHub account (free)
echo     2. Railway account (free tier available)
echo     3. This project uploaded to GitHub
echo.
echo  🚀 STEPS TO DEPLOY:
echo.
echo  STEP 1: Create GitHub Repository
echo     • Go to github.com and create new repository
echo     • Upload all files from this folder to the repository
echo     • Make sure to include: app/, requirements.txt, Procfile, production.py
echo.
echo  STEP 2: Deploy to Railway  
echo     • Go to railway.app
echo     • Sign up/login with GitHub
echo     • Click "New Project" → "Deploy from GitHub repo"
echo     • Select your repository
echo     • Railway will automatically build and deploy!
echo.
echo  STEP 3: Get Your URL
echo     • Railway will provide a URL like: https://yourapp.railway.app
echo     • This URL works from ANY device with internet!
echo     • Share it with anyone who needs access
echo.
echo  💰 COST:
echo     • Free tier: 500 hours/month (plenty for personal use)
echo     • Paid tier: $5/month for unlimited usage
echo.
echo  📱 FEATURES YOU GET:
echo     • ✅ Access from phone, tablet, computer
echo     • ✅ Automatic HTTPS (secure)
echo     • ✅ No installation needed for users
echo     • ✅ Auto-updates when you change code
echo     • ✅ Database and images persist
echo.
echo  🔄 UPDATING:
echo     • Make changes to code
echo     • Push to GitHub
echo     • Railway automatically redeploys!
echo.
echo  ════════════════════════════════════════════════════════════════════════════
echo.
echo  📁 Files ready for deployment:
echo     ✅ Procfile (tells Railway how to start)
echo     ✅ railway.json (Railway configuration)  
echo     ✅ production.py (optimized startup)
echo     ✅ requirements.txt (updated with gunicorn)
echo     ✅ All your app files
echo.
echo  📖 Need detailed help? Check RAILWAY_DEPLOYMENT.md
echo.
echo  Ready to upload to GitHub and deploy to Railway!
echo.
pause
