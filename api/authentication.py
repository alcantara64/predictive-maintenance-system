from fastapi import APIRouter, HTTPException, Depends
from model.pydantic import UserRegistration, UserLogin
from utils.authentication import AuthHandler
from db import database_handler
from config import COLLECTIONS

auth_router = APIRouter()
auth_handler = AuthHandler()

@auth_router.post("/register")
def register(user: UserRegistration):
    existing_user = database_handler.find_documents(collection=COLLECTIONS.get('user'), query={"email": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = auth_handler.hash_password(user.password)
    new_user = {**dict(user), "password": hashed_password}
    database_handler.insert_document(collection=COLLECTIONS.get('user'), document=new_user)
    return {"message": "User registered successfully"}

@auth_router.post("/token")
def login(form_data: UserLogin):
    user = database_handler.find_one_document(collection=COLLECTIONS.get('user'), query={"email": form_data.username})
    if not user or not auth_handler.verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = auth_handler.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}