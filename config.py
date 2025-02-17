from fastapi.security import OAuth2PasswordBearer
import os

COLLECTIONS = {
    'user':'users',
    'sensor':'sensors',
    'prediction': 'predictions',
    'notification': 'notifications'
}
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "predictive_maintenance"

SECRET_KEY = os.getenv("SECRET_KEY","your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")