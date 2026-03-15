# Render Deployment Instructions

## Current Status
- ✅ Backend is running on: https://drag-n-scroll.onrender.com/api
- ✅ Latest code needs to be deployed
- ❌ Auto-deploy from GitHub may not be configured

## How to Deploy Latest Code to Render:

### Option 1: Enable Auto-Deploy (Recommended)
1. Go to: https://dashboard.render.com/
2. Find: drag-n-scroll service
3. Go to: Settings → GitHub
4. Enable: Auto-deploy on push to main branch

### Option 2: Manual Deploy
1. Go to: https://dashboard.render.com/
2. Find: drag-n-scroll service
3. Click: "Manual Deploy"
4. Select: main branch
5. Click: "Deploy latest commit"

### Option 3: Update Render YAML
The render.yaml file is already configured at: backend/render.yaml
Render should automatically pick up this file when connected to GitHub.

## Important Notes:
- Backend URL: https://drag-n-scroll.onrender.com/api
- Frontend is already configured to use this URL
- Vercel backend (drag-n-scroll-backend.vercel.app) can be ignored
