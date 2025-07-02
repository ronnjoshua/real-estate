# Deploy to Vercel (Free Tier)

## Quick Setup

### 1. Frontend (Vercel)
1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and sign up with GitHub
3. Click "Import Project" and select your repository
4. Set these environment variables in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
   ```
5. Deploy!

### 2. Backend (Railway - Free Tier)
1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click "Deploy from GitHub repo" and select your repo
3. Set these environment variables:
   ```
   SECRET_KEY=your-generated-secret-key
   ALLOWED_ORIGINS=["https://your-app.vercel.app"]
   ```
4. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

## File Structure for Deployment
```
/
├── frontend/          # Next.js app (deployed to Vercel)
├── backend/           # FastAPI app (deployed to Railway)
├── vercel.json        # Vercel config (points to frontend)
└── railway.toml       # Railway config (optional)
```

## Environment Variables

### Frontend (.env.local in Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```

### Backend (Railway Environment)
```
SECRET_KEY=your-64-character-secret-key
ALLOWED_ORIGINS=["https://your-frontend.vercel.app"]
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Post-Deployment
1. Update CORS origins in backend to include your Vercel domain
2. Test authentication flow
3. Verify API endpoints work

Your app will be live at:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.railway.app`