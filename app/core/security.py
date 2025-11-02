from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import APIKeyHeader
from fastapi import Depends

api_key_header = APIKeyHeader(name="Authorization")

def user_auth(api_key: str = Depends(api_key_header)):
    return verify_access_token(api_key)

# Secret key & konfigurasi token
SECRET_KEY = "DIWHDWOIHDWOIHDWOIDHWOIDWH"  # ganti dengan secret yang lebih aman
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 525600  # token valid 1 tahun

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") is None:
            return None
        if datetime.fromtimestamp(float(payload.get("exp")), timezone.utc) < datetime.now(timezone.utc):
            return None
        return payload
    except JWTError:
        return None
