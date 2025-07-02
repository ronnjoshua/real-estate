# Deploy Backend to Railway

## Quick Setup

### 1. Prepare Your Repository
Make sure your code is pushed to GitHub with the latest changes.

### 2. Railway Account Setup
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click "Start a New Project"
4. Select "Deploy from GitHub repo"
5. Choose your real-estate repository

### 3. Configure the Deployment

#### Project Settings:
- **Service Name**: `real-estate-backend`
- **Root Directory**: `backend`

Railway will auto-detect the configuration from the files I've created:
- `Procfile` - Defines the start command
- `nixpacks.toml` - Build configuration  
- `runtime.txt` - Python version

**Manual Override (if needed):**
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Environment Variables:
Add these in Railway dashboard under "Variables":

```env
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=["https://your-frontend.vercel.app"]
PORT=8000
```

### 4. Generate Secret Key
Run this locally to generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```
Copy the output and use it as your `SECRET_KEY`.

### 5. Deploy Process
1. Railway will automatically detect it's a Python project
2. It will install dependencies from `requirements.txt`
3. Start the FastAPI server on the assigned port
4. Your API will be available at: `https://your-project.railway.app`

### 6. Post-Deployment Setup

#### Update Frontend Environment:
In Vercel, update your environment variable:
```
NEXT_PUBLIC_API_URL=https://your-project.railway.app/api/v1
```

#### Test Your Deployment:
- Visit: `https://your-project.railway.app/docs` (API documentation)
- Check: `https://your-project.railway.app/api/v1/properties` (should return empty array)

### 7. Custom Domain (Optional)
1. In Railway dashboard, go to Settings → Domains
2. Add your custom domain
3. Update CORS origins accordingly

## Troubleshooting

### Common Issues:

**1. Build Fails**
```bash
# Check requirements.txt is in backend folder
# Ensure Python version compatibility
```

**2. Server Won't Start**
```bash
# Verify start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
# Check that app.main:app path is correct
```

**3. CORS Errors**
```bash
# Update ALLOWED_ORIGINS to include your Vercel domain
# Format: ["https://your-app.vercel.app"]
```

**4. Environment Variables**
```bash
# Ensure SECRET_KEY is set and not the default
# Verify all required variables are added in Railway
```

## Railway CLI (Optional)

Install Railway CLI for easier management:
```bash
# Install
npm install -g @railway/cli

# Login
railway login

# Deploy from local
railway up
```

## Free Tier Limits
- 500 hours per month
- $5 credit monthly
- Automatic sleep after inactivity
- 1GB memory, 1 vCPU

Your FastAPI backend will be live at Railway and ready to serve your Vercel frontend!