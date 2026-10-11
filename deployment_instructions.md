# Deployment Instructions

This guide provides step-by-step instructions for deploying the Stock Market Analysis and Prediction System.

## Prerequisites

- Docker and Docker Compose
- Git
- Python 3.11+ (for local development)
- PostgreSQL (optional, for production)

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd visionary
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run Database Migrations
```bash
# Tables are created automatically when the app starts
# For manual migration, you can use alembic if configured
```

### 6. Run the Application

#### Option A: Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

#### Option B: Manual Setup

Terminal 1 - FastAPI Backend:
```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2 - Streamlit Frontend:
```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

### 7. Access the Application
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Production Deployment

### Docker Deployment

#### 1. Build and Run with Docker Compose
```bash
# For development
docker-compose -f docker-compose.yml up --build

# For production with PostgreSQL
docker-compose -f docker-compose.prod.yml up --build
```

#### 2. Environment Configuration
Update the `.env` file with production values:
```env
DATABASE_URL=postgresql://user:password@db/stock_analysis
SECRET_KEY=your-production-secret-key
FASTAPI_SERVER_PORT=8000
STREAMLIT_SERVER_PORT=8501
```

### Railway Deployment

#### 1. Create Railway Account
Sign up at https://railway.app

#### 2. Connect Repository
```bash
# Push your code to GitHub
git add .
git commit -m "Initial commit"
git push origin main
```

#### 3. Deploy on Railway
1. Connect your GitHub repository
2. Add environment variables in Railway dashboard
3. Railway will automatically detect and build the Docker container
4. Access your app at the provided Railway URL

### Render Deployment

The repository includes a `render.yaml` Blueprint for the FastAPI API, Streamlit
frontend, and PostgreSQL database.

1. Push the project to a GitHub repository. Ensure `.env` is not committed; set
   `SECRET_KEY` and `ALPHA_VANTAGE_API_KEY` through Render instead.
2. In the Render dashboard choose **New +** → **Blueprint** and connect the repo.
3. Review the resources detected from `render.yaml` and apply the Blueprint.
4. When prompted for `ALPHA_VANTAGE_API_KEY`, enter your own Alpha Vantage key
   (or leave it blank if you do not use Alpha Vantage).
5. Wait for the API, database, and frontend deployments to finish.
6. Open the frontend service URL. Check the API at
   <https://stock-analysis-api-0dqg.onrender.com/health> and its docs at
   <https://stock-analysis-api-0dqg.onrender.com/docs>.

The deployed API base URL is <https://stock-analysis-api-0dqg.onrender.com>.
The frontend Blueprint service reads the API service hostname and adds HTTPS
automatically through `FASTAPI_URL`. For a separate Streamlit deployment, set
its `FASTAPI_URL` environment variable to the API base URL above. Render-generated
`SECRET_KEY` and database connection settings are wired through the Blueprint.
Free Render web services may sleep when idle; free PostgreSQL databases have
limited retention, so choose an appropriate paid persistent database for
production data.

### Streamlit Cloud Deployment

The FastAPI backend stays hosted on Render; Streamlit Community Cloud hosts only
the dashboard.

1. Push the completed frontend changes to the GitHub branch you want to deploy.
2. Sign in at <https://share.streamlit.io> with GitHub and choose **Create app**.
3. Select repository `shukla-2005/visionary`, branch `master`, and main file
   `frontend/streamlit_app.py`.
4. In **Advanced settings**, select Python **3.10** to match the project's pinned
   dependencies.
5. Before deploying, add the following to the app's **Secrets**:

   ```toml
   FASTAPI_URL = "https://stock-analysis-api-0dqg.onrender.com"
   ```

6. Deploy the app and open the URL provided by Streamlit Community Cloud.
7. Test login/registration and a market-data action. The Render API may need up
   to 90 seconds to respond after sleeping.

The frontend reads `FASTAPI_URL` from Streamlit secrets or an environment
variable. Do not commit secrets or credentials to the repository.

### Heroku Deployment

#### 1. Create Heroku Account
Sign up at https://heroku.com

#### 2. Install Heroku CLI
```bash
# Download and install from https://devcenter.heroku.com/articles/heroku-cli
```

#### 3. Prepare for Heroku
```bash
# Create requirements.txt (already done)
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

#### 4. Deploy
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url
git push heroku main
```

## Environment Variables

### Required Variables
```env
DATABASE_URL=sqlite:///./stock_analysis.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FASTAPI_SERVER_PORT=8000
STREAMLIT_SERVER_PORT=8501
```

### Optional Variables
```env
YAHOO_FINANCE_API_KEY=your-key-if-needed
POSTGRES_DB=stock_analysis
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

## Database Setup

### SQLite (Default)
- No additional setup required
- Database file created automatically

### PostgreSQL
```bash
# Using Docker
docker run --name postgres-stock -e POSTGRES_DB=stock_analysis -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Or install PostgreSQL locally
# Then update DATABASE_URL in .env
```

## SSL/TLS Configuration

For production deployments, ensure HTTPS is enabled:

- Railway: Automatic HTTPS
- Render: Automatic HTTPS
- Heroku: Automatic HTTPS
- Docker: Configure reverse proxy (nginx) with SSL certificates

## Monitoring and Logging

### Application Logs
```bash
# View FastAPI logs
docker-compose logs fastapi

# View Streamlit logs
docker-compose logs streamlit
```

### Health Checks
- API Health: `GET /health`
- Database connectivity check built into startup

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use Redis for session storage if needed
- Consider database connection pooling

### Performance Optimization
- Use PostgreSQL in production
- Implement caching for frequently accessed data
- Optimize ML model loading
- Use CDN for static assets

## Backup Strategy

### Database Backup
```bash
# SQLite
cp stock_analysis.db stock_analysis_backup.db

# PostgreSQL
pg_dump stock_analysis > backup.sql
```

### Model Backup
```bash
# Backup saved models
cp -r saved_models saved_models_backup
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml or .env
2. **Database connection**: Check DATABASE_URL format
3. **Memory issues**: Increase Docker memory limits
4. **ML model loading**: Ensure models are saved correctly

### Debug Mode
```bash
# Run with debug logging
docker-compose up --build --force-recreate
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong passwords
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Validate input data
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor for vulnerabilities

## Cost Estimation

### Free Tier Limits
- Railway: $5/month free credit
- Render: 750 hours/month free
- Heroku: 550 hours/month free
- Streamlit Cloud: Unlimited free for public apps

### Paid Plans
- Railway: $5-15/month
- Render: $7-29/month
- Heroku: $7-25/month

## Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Test API endpoints individually
4. Check network connectivity
5. Review deployment platform documentation