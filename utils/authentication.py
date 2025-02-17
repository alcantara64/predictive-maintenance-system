
import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, COLLECTIONS, DATABASE_NAME, MONGO_URI, SECRET_KEY,oauth2_scheme
from db import database_handler





class AuthHandler:
    def __init__(self):
        pass
        

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        :param password: The plaintext password.
        :return: The hashed password.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a hashed password.

        :param plain_password: The plaintext password.
        :param hashed_password: The hashed password.
        :return: True if the passwords match, False otherwise.
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, data: dict) -> str:
        """
        Create a JWT access token.

        :param data: The data to encode in the token (e.g., username).
        :return: The encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token.

        :param token: The JWT token to decode.
        :return: The decoded token payload.
        :raises HTTPException: If the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    async def get_current_user(self,token: str = Depends(oauth2_scheme)):
      try:
          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
          username: str = payload.get("sub")
          if username is None:
              raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
      except jwt.ExpiredSignatureError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
      except jwt.InvalidTokenError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
      user = database_handler.find_one_document(collection=COLLECTIONS.get('user'), query={"username":username})
      if user is None:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
      return user