# GitHub & Vercel Deployment Guide

## Step 1: Initialize Git Repository

```bash
cd /Users/jamescollins/Downloads/csv-filter-tool
git init
git add .
git commit -m "Initial commit: CSV converter tool"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Name: `csv-filter-tool`
3. Description: "Convert Next Day Service Appointment CSV exports"
4. Choose: Public (to deploy on Vercel)
5. Click "Create repository"

## Step 3: Push to GitHub

After creating the repo, GitHub will show you commands. Run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/csv-filter-tool.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 4: Deploy to Vercel

1. Go to https://vercel.com (sign up/login with GitHub)
2. Click "New Project"
3. Select "Import Git Repository"
4. Find and select `csv-filter-tool`
5. Click "Import"
6. Vercel auto-detects Flask app → Click "Deploy"
7. Wait for deployment to complete
8. You'll get a URL like: `https://csv-filter-tool-xyz.vercel.app`

## Step 5: Share

Your web app is now live! Share the Vercel URL with others.

## Updates

When you make changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Vercel automatically redeploys!

## Local Testing

Before deploying, test locally:

```bash
cd /Users/jamescollins/Downloads/csv-filter-tool
pip install -r requirements.txt
python3 app.py
```

Then visit: http://localhost:5000
