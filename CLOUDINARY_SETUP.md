# Cloudinary Setup for Persistent Image Storage

## Why Cloudinary?
Railway uses ephemeral storage, meaning uploaded files are deleted when the app restarts or redeploys. Cloudinary provides free cloud storage for images.

## Setup Instructions:

### 1. Create Cloudinary Account
1. Go to https://cloudinary.com
2. Sign up for a free account
3. Note your Cloud Name, API Key, and API Secret from the dashboard

### 2. Configure Railway Environment Variable
1. Go to your Railway project dashboard
2. Click on "Variables" tab
3. Add this environment variable:
   ```
   CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
   ```
   Replace API_KEY, API_SECRET, and CLOUD_NAME with your actual values

### 3. How It Works
- **With Cloudinary**: Images are uploaded to Cloudinary cloud storage and persist forever
- **Without Cloudinary**: Images are stored locally on Railway (lost on restart) 
- **Local Development**: Always uses local storage in `/data/uploads/`

### 4. Free Tier Limits
- 25 credits per month (plenty for a personal app)
- 25GB storage 
- 25GB monthly bandwidth

## Current Status
The app now supports both storage methods:
- ✅ Cloudinary URLs (starts with `http`) - displayed directly
- ✅ Local filenames - served through `/uploads/` route
- ✅ Missing images - shows "Image Missing" warning instead of breaking

## Testing
1. Deploy to Railway with `CLOUDINARY_URL` environment variable
2. Add a new board with images
3. Images should now persist even after app restarts!
