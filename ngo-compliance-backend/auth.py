from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "ngo-compliance-pilot-secret"  # fine for pilot, env var in production
ALGORITHM  = "HS256"

# Hardcoded pilot users — no database, no signup
PILOT_USERS = {
    "officer@darpan.gov.in": {
        "password": "pilot2025",
        "name":     "Officer Ramesh Kumar",
        "role":     "compliance_officer"
    },
    "admin@darpan.gov.in": {
        "password": "admin2025",
        "name":     "Admin",
        "role":     "admin"
    },
}

def login(email: str, password: str) -> dict:
    user = PILOT_USERS.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({
        "sub":   email,
        "name":  user["name"],
        "role":  user["role"],
        "exp":   datetime.utcnow() + timedelta(hours=8)
    }, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"token": token, "name": user["name"], "role": user["role"]}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY,
                             algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")