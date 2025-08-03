# Railway Deployment Guide with Persistent Database

## The Problem
Railway (like most cloud platforms) has an **ephemeral file system** - any files created during runtime get deleted when you redeploy your code. This includes your SQLite database and uploaded images.

## The Solution
Use Railway's **PostgreSQL service** for persistent data storage.

## Step-by-Step Setup

### 1. Add PostgreSQL Service to Railway

1. Go to your Railway project dashboard
2. Click **"+ Add Service"**
3. Select **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically create a PostgreSQL database and provide connection details

### 2. Update Your Code

Your code has been updated to support both PostgreSQL (Railway) and SQLite (local development). No manual changes needed!

### 3. Deploy the Updated Code

```bash
# Make sure all files are committed
git add .
git commit -m "Add PostgreSQL support for Railway deployment"
git push origin main
```

### 4. Environment Variables (Automatic)

Railway automatically sets these environment variables when you add PostgreSQL:
- `DATABASE_URL` - PostgreSQL connection string
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` - Individual components

### 5. Update Procfile (Already Done)

Your `Procfile` now uses the Railway-optimized production script:
```
web: python railway_production.py
```

## What Happens Now

### On Railway (Production):
- ✅ Uses PostgreSQL database (persistent across deployments)
- ✅ Data survives code updates
- ✅ Multiple users can access simultaneously
- ✅ Professional-grade database performance

### On Your Local Machine:
- ✅ Still uses SQLite (easy development)
- ✅ Your existing data is preserved
- ✅ No setup required for local development

## File Storage Note

**Images are still ephemeral on Railway's free tier.** For a complete solution, you would need:

1. **Railway Pro Plan** - Provides persistent file storage
2. **Cloud Storage** (AWS S3, Cloudinary, etc.) - Store images externally

For now, images will be lost on redeploy, but your **database data (boards, players, games) will persist**.

## Testing Your Deployment

1. Deploy your updated code
2. Add some boards and players
3. Redeploy your code (make a small change and push)
4. Check that your boards and players are still there ✅

## Backup Strategy

Even with PostgreSQL, it's good practice to backup:

```bash
# Local backup (still works)
python backup_data.py

# Railway database backup (automatic)
# Railway automatically backs up PostgreSQL databases
```

## Cost Information

- **PostgreSQL on Railway**: $5/month
- **Worth it because**: Your data persists forever, no more losing boards/players/games!

## Troubleshooting

If deployment fails:
1. Check Railway logs in the dashboard
2. Ensure all requirements are in `requirements.txt`
3. Verify `railway_production.py` is being used in `Procfile`

Your cribbage board collection will now survive all code updates! 🎉
