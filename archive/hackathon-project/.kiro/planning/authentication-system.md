# Authentication & User Management System

## Authentication Strategy

### User Authentication Flow
```
Registration → Email Verification → Login → JWT Token → Protected Routes
```

### Authentication Methods
1. **Email/Password** (Primary)
2. **Google OAuth** (Future enhancement)
3. **LinkedIn OAuth** (Future enhancement for professional users)

### JWT Token Strategy
```typescript
interface JWTPayload {
  user_id: string;
  email: string;
  subscription_tier: 'free' | 'pro' | 'elite';
  permissions: string[];
  exp: number;
  iat: number;
}
```

### Token Management
- **Access Token:** 15 minutes expiry
- **Refresh Token:** 7 days expiry
- **Secure Storage:** HttpOnly cookies + localStorage backup
- **Token Rotation:** Automatic refresh before expiry

## User Management Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_status VARCHAR(20) DEFAULT 'active',
    subscription_expires_at TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier, subscription_status);
CREATE INDEX idx_users_verification ON users(email_verification_token);
```

### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cleanup expired sessions
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Example preferences structure
{
  "dashboard": {
    "default_view": "recent_reports",
    "charts_per_page": 10
  },
  "reports": {
    "default_sections": ["executive_summary", "financials", "valuation"],
    "chart_style": "professional",
    "export_format": "pdf"
  },
  "notifications": {
    "email_reports": true,
    "price_alerts": false
  }
}
```

## Subscription Management

### Subscription Tiers
```typescript
interface SubscriptionTier {
  name: 'free' | 'pro' | 'elite';
  price_monthly: number;
  reports_per_month: number;
  features: string[];
  storage_gb: number;
}

const SUBSCRIPTION_TIERS = {
  free: {
    name: 'free',
    price_monthly: 0,
    reports_per_month: 1,
    features: ['basic_reports', 'pdf_export'],
    storage_gb: 1
  },
  pro: {
    name: 'pro', 
    price_monthly: 49,
    reports_per_month: 10,
    features: ['comprehensive_reports', 'interactive_charts', 'scenario_modeling'],
    storage_gb: 10
  },
  elite: {
    name: 'elite',
    price_monthly: 149,
    reports_per_month: -1, // unlimited
    features: ['all_features', 'priority_support', 'custom_analysis'],
    storage_gb: 100
  }
};
```

### Usage Tracking
```sql
CREATE TABLE user_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    usage_type VARCHAR(50) NOT NULL, -- 'report_generation', 'storage', 'api_calls'
    usage_amount INTEGER NOT NULL,
    usage_date DATE NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track monthly usage
CREATE INDEX idx_usage_user_date ON user_usage(user_id, usage_date);
CREATE INDEX idx_usage_type ON user_usage(usage_type, usage_date);
```

## Security Implementation

### Password Security
```python
import bcrypt
import secrets

class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_secure_token() -> str:
        return secrets.token_urlsafe(32)
```

### Rate Limiting
```python
from fastapi import HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Authentication endpoints rate limiting
@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginCredentials):
    # Login logic with rate limiting
    pass

@app.post("/auth/register") 
@limiter.limit("3/hour")
async def register(request: Request, user_data: UserRegistration):
    # Registration logic with rate limiting
    pass
```

### Input Validation
```python
from pydantic import BaseModel, EmailStr, validator
import re

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain number')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not re.match(r'^[a-zA-Z\s-]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
```

## Email Verification System

### Email Service Integration
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")
    
    async def send_verification_email(self, user_email: str, token: str):
        verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to MarketMind Pro!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <a href="{verification_url}">Verify Email Address</a>
            <p>This link will expire in 24 hours.</p>
        </body>
        </html>
        """
        
        await self._send_email(user_email, "Verify Your Email", html_content)
```

### Verification Flow
```python
@app.post("/auth/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email_verification_token == token,
        User.email_verified == False
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    user.email_verified = True
    user.email_verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully"}
```

## User Profile Management

### Profile Update API
```python
class UserProfileUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    preferences: Optional[dict]

@app.put("/users/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_data.first_name:
        current_user.first_name = profile_data.first_name
    if profile_data.last_name:
        current_user.last_name = profile_data.last_name
    
    if profile_data.preferences:
        # Update user preferences
        prefs = db.query(UserPreferences).filter(
            UserPreferences.user_id == current_user.id
        ).first()
        if prefs:
            prefs.preferences = profile_data.preferences
        else:
            prefs = UserPreferences(
                user_id=current_user.id,
                preferences=profile_data.preferences
            )
            db.add(prefs)
    
    db.commit()
    return {"message": "Profile updated successfully"}
```

## Frontend Authentication Integration

### Auth Context Provider
```typescript
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Check for existing token on app load
    const token = localStorage.getItem('access_token');
    if (token) {
      validateToken(token);
    } else {
      setIsLoading(false);
    }
  }, []);
  
  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', {email, password});
    const {access_token, refresh_token, user} = response.data;
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    setUser(user);
  };
  
  // ... other auth methods
};
```

### Protected Route Component
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredTier?: 'free' | 'pro' | 'elite';
  fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredTier,
  fallback
}) => {
  const {user, isAuthenticated, isLoading} = useAuth();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (requiredTier && !hasRequiredTier(user?.subscription_tier, requiredTier)) {
    return fallback || <UpgradePrompt requiredTier={requiredTier} />;
  }
  
  return <>{children}</>;
};
```

*Last Updated: 2026-01-22*
