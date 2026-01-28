# MarketMind Pro - JWT Authentication System

## Overview

This implementation provides a minimal but functional JWT authentication system that replaces the hardcoded `user_id = 1` throughout the MarketMind Pro application.

## Key Features

✅ **JWT Token Authentication** - Secure token-based authentication
✅ **User Registration & Login** - Complete user management
✅ **Protected Endpoints** - All report endpoints now require authentication
✅ **User Ownership** - Users can only access their own reports
✅ **Minimal Implementation** - Only essential code, no bloat

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements-auth.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

### 3. Update Environment Variables
Add to your `.env` file:
```env
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Start the Application
```bash
uvicorn app.main:app --reload
```

## Usage Examples

### Register a New User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Generate Report (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/reports/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ticker": "AAPL",
    "report_type": "comprehensive"
  }'
```

## What Changed

### 1. Authentication Dependencies (`app/core/auth.py`)
- `get_current_user()` - Validates JWT tokens and returns user
- `get_current_active_user()` - Ensures user is active
- `get_current_user_optional()` - Optional authentication

### 2. Updated Endpoints
- **Reports Router** (`app/features/reports/router.py`)
  - All endpoints now require authentication
  - Users can only access their own reports
  
- **Production Router** (`app/api/production_router.py`)
  - Report generation includes user context
  - Report IDs now include user ID for ownership
  
- **Main App** (`app/main.py`)
  - PDF endpoints require authentication
  - User ownership validation

### 3. Database Models
- User model already existed in `app/features/auth/models.py`
- No database schema changes needed

## Security Features

- **JWT Tokens** - Secure, stateless authentication
- **Password Hashing** - bcrypt for secure password storage
- **User Ownership** - Users can only access their own data
- **Token Expiration** - Configurable token lifetime
- **Input Validation** - Pydantic models for request validation

## Testing

Run the test script to verify everything works:
```bash
python test_auth.py
```

## Migration from Hardcoded user_id = 1

The system now:
1. ❌ **Before**: `user_id = 1` hardcoded everywhere
2. ✅ **After**: `current_user.id` from JWT token

All existing functionality remains the same, but now properly authenticated and user-scoped.

## Production Considerations

1. **Change JWT Secret**: Use a strong, unique secret key
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Storage**: Store tokens securely on the client side
4. **Rate Limiting**: Consider adding rate limiting for auth endpoints
5. **Refresh Tokens**: Consider implementing refresh tokens for longer sessions

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check if token is included in Authorization header
2. **403 Forbidden**: User trying to access another user's resources
3. **Token Expired**: Login again to get a new token

### Debug Mode
Set `DEBUG=True` in your environment to see detailed error messages.

---

**The authentication system is now fully functional and secure!** 🔐