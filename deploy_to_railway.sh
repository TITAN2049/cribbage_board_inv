#!/bin/bash
# Railway Deployment Script with PostgreSQL Setup

echo "================================================================"
echo "        RAILWAY DEPLOYMENT WITH PERSISTENT DATABASE"
echo "================================================================"
echo ""

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo "❌ This is not a git repository. Initializing..."
    git init
    git add .
    git commit -m "Initial commit"
    echo "✅ Git repository initialized"
fi

echo "🔍 Checking Railway CLI..."
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    echo "Run this command to install Railway CLI:"
    echo "npm install -g @railway/cli"
    echo ""
    echo "Or visit: https://railway.app/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

echo "🔄 Step 1: Login to Railway"
railway login

echo ""
echo "🔄 Step 2: Creating new Railway project..."
railway init

echo ""
echo "🔄 Step 3: Adding PostgreSQL database..."
echo "This will add a PostgreSQL database to your Railway project"
echo "The database will cost $5/month but your data will persist forever!"
echo ""
read -p "Add PostgreSQL database? (y/n): " add_db

if [[ $add_db == "y" || $add_db == "Y" ]]; then
    echo "Adding PostgreSQL..."
    railway add -d postgresql
    echo "✅ PostgreSQL added!"
    echo ""
    echo "⚠️  Note: This will cost $5/month, but your data will be safe!"
else
    echo "⚠️  Skipping PostgreSQL - your data will be lost on every deployment!"
fi

echo ""
echo "🔄 Step 4: Committing updated code..."
git add .
git commit -m "Add PostgreSQL support for Railway deployment"

echo ""
echo "🔄 Step 5: Deploying to Railway..."
railway up

echo ""
echo "================================================================"
echo "                    DEPLOYMENT COMPLETE!"
echo "================================================================"
echo ""
echo "✅ Your cribbage board collection is now deployed to Railway!"
echo ""
echo "🌐 Get your app URL:"
echo "   railway domain"
echo ""
echo "📊 Check your deployment:"
echo "   railway status"
echo ""
echo "📝 View logs:"
echo "   railway logs"
echo ""
echo "💾 Database Status:"
if [[ $add_db == "y" || $add_db == "Y" ]]; then
    echo "   ✅ PostgreSQL database added - data will persist!"
    echo "   💰 Cost: $5/month for persistent storage"
else
    echo "   ⚠️  No database added - data will be lost on redeploy"
    echo "   💡 Add PostgreSQL later with: railway add -d postgresql"
fi
echo ""
echo "🎉 Your app is live and ready to use!"
echo ""
