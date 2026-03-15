# Render Webhook Configuration

## Webhook for Auto-Deploy
Add this webhook URL to your GitHub repository settings to trigger automatic Render deployments:

### How to Setup:
1. Get your Render Service ID from: https://dashboard.render.com/
2. Go to your GitHub repo: Settings → Webhooks → Add webhook
3. Use this URL pattern: `https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys`

## Or Enable Auto-Deploy in Render Dashboard:
1. Go to: https://dashboard.render.com/
2. Open your service: drag-n-scroll
3. Go to: Settings → Git
4. Enable: "Auto-deploy on push to main branch"

## Quick Deploy Command:
After pushing to GitHub, go to:
https://dashboard.render.com/blueprints/ctrl/deploy

Or manually trigger deploy from service dashboard.
