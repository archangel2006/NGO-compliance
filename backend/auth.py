# backend/auth.py

import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY   = os.getenv("JWT_SECRET", "ngo-compliance-pilot-secret-2025")
ALGORITHM    = "HS256"
EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 8))

# Hardcoded pilot users — no DB, no signup
PILOT_USERS = {
    "officer@darpan.gov.in": {
        "password": "pilot2025",
        "name":     "Officer Ramesh Kumar",
        "role":     "compliance_officer",
    },
    "admin@darpan.gov.in": {
        "password": "admin2025",
        "name":     "Admin",
        "role":     "admin",
    },
}

bearer_scheme = HTTPBearer()


def login(email: str, password: str) -> dict:
    user = PILOT_USERS.get(email.lower().strip())
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {
            "sub":   email,
            "name":  user["name"],
            "role":  user["role"],
            "exp":   datetime.utcnow() + timedelta(hours=EXPIRE_HOURS),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {
        "token":     token,
        "name":      user["name"],
        "role":      user["role"],
        "email":     email,
        "expires_in": EXPIRE_HOURS * 3600,
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def require_officer(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") not in ("compliance_officer", "admin"):
        raise HTTPException(status_code=403, detail="Officer access required.")
    return user