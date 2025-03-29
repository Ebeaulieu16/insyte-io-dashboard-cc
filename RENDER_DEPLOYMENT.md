# Render Deployment Guide

This guide outlines how to properly deploy the Insyte.io Dashboard to Render.

## Setting up your Frontend Deployment

1. Create a new Web Service in Render
2. Connect your GitHub repository
3. Use these settings:
   - **Name**: insyte-io-dashboard
   - **Environment**: Static Site
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`

### Frontend Environment Variables

Set these in the Render dashboard under Environment:

```
REACT_APP_API_URL=https://api.insyte.io
REACT_APP_BASE_URL=https://insyte.io
```

## Setting up your Backend Deployment

1. Create a new Web Service in Render
2. Connect your GitHub repository
3. Use these settings:
   - **Name**: api-insyte-io
   - **Environment**: Python
   - **Build Command**: `pip install -r backend/requirements.txt && cd backend && alembic upgrade head`
   - **Start Command**: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Backend Environment Variables

Set these in the Render dashboard under Environment:

```
# Database configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/insyte_dashboard
# For Render-managed PostgreSQL, this is provided automatically when linked

# Application settings
APP_URL=https://api.insyte.io
FRONTEND_URL=https://insyte.io

# YouTube API credentials
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# Stripe API credentials
STRIPE_API_KEY=your_stripe_api_key
STRIPE_CLIENT_ID=your_stripe_client_id
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Calendly API credentials
CALENDLY_CLIENT_ID=your_calendly_client_id
CALENDLY_CLIENT_SECRET=your_calendly_client_secret
CALENDLY_API_KEY=your_calendly_api_key

# Cal.com API credentials
CALCOM_CLIENT_ID=your_calcom_client_id
CALCOM_CLIENT_SECRET=your_calcom_client_secret
CALCOM_API_KEY=your_calcom_api_key

# JWT Secret for token encryption
JWT_SECRET=generate_a_secure_random_string_here
```

## Setting up a Render PostgreSQL Database

1. Create a new PostgreSQL database in Render
2. Link it to your backend service
3. Render will automatically add the `DATABASE_URL` environment variable

## Important OAuth Configuration Steps

### 1. Update OAuth Redirect URIs

In each third-party integration dashboard (YouTube, Stripe, etc.), update your OAuth redirect URIs:

- YouTube: `https://api.insyte.io/auth/youtube/callback`
- Stripe: `https://api.insyte.io/auth/stripe/callback`
- Calendly: `https://api.insyte.io/auth/calendly/callback`
- Cal.com: `https://api.insyte.io/auth/calcom/callback`

### 2. Stripe Webhook Configuration

1. In your Stripe dashboard, create a webhook pointing to:
   `https://api.insyte.io/webhook/stripe`
2. Select the `payment_intent.succeeded` event
3. Copy the signing secret and add it as `STRIPE_WEBHOOK_SECRET` in your backend environment variables

## Troubleshooting

If you encounter integration issues:

1. **Check Environment Variables**: Ensure all required variables are set correctly
2. **Check OAuth Settings**: Verify redirect URIs are properly configured in each platform
3. **Inspect Logs**: Review service logs in the Render dashboard for error messages
4. **Test API Endpoints**: Make sure the backend endpoints respond correctly
5. **CORS Issues**: Verify FRONTEND_URL in the backend matches your actual frontend URL

## Security Considerations

- Never commit actual API keys or secrets to your Git repository
- Generate a strong random string for JWT_SECRET
- Use Render's environment variables feature for all sensitive information
- Consider setting up IP restrictions for your database
