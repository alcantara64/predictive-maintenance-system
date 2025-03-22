from fastapi import APIRouter, HTTPException, Depends
from model.pydantic import UserRegistration, UserLogin
from utils.authentication import AuthHandler
from db import database_handler
from config import COLLECTIONS

user_router = APIRouter()

@user_router.get("/")
async def get_users():
    users = database_handler.find_documents(collection=COLLECTIONS.get('user'))
    return users 
