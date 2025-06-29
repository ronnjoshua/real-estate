# Real Estate Platform - Deployment Guide

## 🚀 Quick Start (Development)

### Prerequisites
- Node.js 18+ 
- Python 3.11+
- Firebase account (optional for full features)

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
```

5. **Generate secure secret key**
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
```
Copy the output and replace the SECRET_KEY in `.env`

6. **Start the backend server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.local.example .env.local
```

4. **Start the development server**
```bash
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔐 Authentication

### Default Admin User
For development, the system uses in-memory storage. You can create users via:

```bash
# Use the API endpoint or run the admin script
python3 scripts/manage_users.py create-admin admin@example.com "AdminPass123!" "Admin User"
```

### Security Features Implemented
- ✅ JWT-based authentication with refresh tokens
- ✅ Secure sessionStorage token management
- ✅ Password strength validation
- ✅ Role-based access control (Admin/Client)
- ✅ Rate limiting framework
- ✅ Input validation and sanitization

## 🏢 Production Deployment

### Environment Variables Required

**Backend (.env)**
```env
# Security (REQUIRED)
SECRET_KEY=your-64-character-secure-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Firebase (REQUIRED for production)
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Optional
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NODE_ENV=production
```

### Docker Deployment

**Backend Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

**Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    volumes:
      - ./backend:/app
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### Cloud Deployment Options

#### 1. Vercel + Railway
- **Frontend**: Deploy to Vercel (automatic from GitHub)
- **Backend**: Deploy to Railway with environment variables
- **Database**: Firebase Firestore (managed)

#### 2. AWS
- **Frontend**: S3 + CloudFront
- **Backend**: ECS or Lambda
- **Database**: Firestore or DynamoDB

#### 3. Google Cloud Platform
- **Frontend**: Cloud Storage + CDN
- **Backend**: Cloud Run
- **Database**: Firestore (native)

## 🔧 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/token` - Login (get access/refresh tokens)
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/register` - Register new user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout

### Property Endpoints
- `GET /api/v1/properties` - List properties with filtering
- `GET /api/v1/properties/search` - Search properties
- `GET /api/v1/properties/{id}` - Get property details
- `POST /api/v1/properties` - Create property (auth required)
- `PUT /api/v1/properties/{id}` - Update property (auth required)
- `DELETE /api/v1/properties/{id}` - Delete property (auth required)

### Advanced Filtering
The API supports comprehensive filtering:
- Property type, status, price range
- Bedrooms, bathrooms, area range
- Location (city, state, zip code)
- Features (garage, pool, garden, pet-friendly)
- Year built range
- Sorting by multiple fields

## 📱 Features Implemented

### ✅ Security & Authentication
- JWT authentication with refresh tokens
- Role-based access control (Admin/Client)
- Secure token storage (sessionStorage)
- Password strength validation
- Input sanitization and validation

### ✅ Property Management
- Comprehensive property data model
- Advanced search and filtering (20+ criteria)
- Image and media support
- Status tracking (available, sold, pending, etc.)
- Location-based search

### ✅ User Interface
- Responsive design (mobile-first)
- Mobile navigation menu
- Advanced property filters with collapsible UI
- Professional property cards
- Search functionality with real-time results
- Pagination and infinite scroll

### ✅ API Architecture
- RESTful design with proper HTTP status codes
- Automatic API documentation (FastAPI Swagger)
- Request/response validation with Pydantic
- Error handling and logging
- CORS configuration

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:e2e
```

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Property creation and editing (admin)
- [ ] Property search and filtering
- [ ] Mobile responsiveness
- [ ] Authentication flow
- [ ] Error handling

## 🚨 Security Checklist

### ✅ Implemented
- JWT secret from environment variables
- Token expiration and refresh
- Password hashing with bcrypt
- Input validation on all endpoints
- CORS configuration
- Secure token storage

### 🔄 Recommended for Production
- [ ] Rate limiting implementation (Redis required)
- [ ] API key authentication for external integrations
- [ ] SSL/TLS termination
- [ ] Web Application Firewall (WAF)
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] Database query optimization and indexing
- [ ] Monitoring and alerting
- [ ] Backup and disaster recovery

## 📊 Performance Optimization

### Current Optimizations
- Next.js automatic code splitting
- Image optimization with Next.js Image component
- Lazy loading and pagination
- Efficient API queries with filtering
- Compressed responses

### Production Recommendations
- CDN for static assets
- Redis caching layer
- Database indexing optimization
- Image compression and WebP support
- Service worker for offline functionality

## 🐛 Troubleshooting

### Common Issues

**1. "SECRET_KEY not found" Error**
```bash
# Generate a new secret key
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
# Add to .env file: SECRET_KEY=generated-key-here
```

**2. Firebase Connection Issues**
- Verify Firebase credentials in .env file
- Check Firebase project settings
- Ensure Firestore is enabled in Firebase console

**3. CORS Errors**
- Update ALLOWED_ORIGINS in backend .env
- Verify frontend URL is included in CORS settings

**4. Module Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Support

For deployment issues or questions:
1. Check the logs: `docker-compose logs` or application logs
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check API documentation at `/docs` endpoint

## 🔄 Updates and Maintenance

### Database Migrations
When updating property models:
1. Update Pydantic models in `app/models/`
2. Test with development data
3. Deploy backend changes
4. Update frontend interfaces if needed

### Security Updates
- Regularly update dependencies
- Monitor for security advisories
- Rotate JWT secrets periodically
- Review access logs

This deployment guide ensures a secure, scalable real estate platform deployment following industry best practices.