from app import database
from app.models import User
from contextvars import Token
import os
from fastapi import FastAPI
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import jwt
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app import models, schemas, database, utils
# Trigger server reload to recreate database tables
load_dotenv()

models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()


SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
FRONTEND_URL = os.environ.get("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY)



oauth=OAuth()
oauth.register(
    name ='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs = {
        'scope': 'openid email profile'
    }   
)

@app.get("/api/auth/login")
async def login(request:Request):
    redirect_uri = str(request.url_for('auth_callback'))
    # Ensure HTTPS is used when deployed behind a proxy like Render
    if request.headers.get("x-forwarded-proto") == "https" or "onrender.com" in redirect_uri:
        redirect_uri = redirect_uri.replace("http://", "https://", 1)
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_callback(request:Request, db: Session = Depends(database.get_db)):
    try:
        token= await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        oauth_id = user_info["sub"]
        email = user_info["email"]
        name = user_info.get("name")
        avatar = user_info.get("picture")

        user = db.query(User).filter(User.oauth_id == oauth_id).first()
        if not user:
            user =User(
                auth_provider="google",
                oauth_id=oauth_id,
                email =email,
                name =name,
                avatar =avatar
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.name = name 
            user.avatar = avatar
            db.commit()

        jwt_payload = {
            'sub':user_info['email'],
            'name':user_info.get('name'),
            'exp':datetime.utcnow() + timedelta(hours=24)
        }
        fronntend_token = jwt.encode(jwt_payload,SECRET_KEY,algorithm="HS256")
        return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?token={fronntend_token}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400,detail = f"Authentication failed :{str(e)}")

@app.post("/api/auth/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = utils.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, auth_provider="local")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login/local")
def login_local(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or db_user.auth_provider != "local" or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    
    jwt_payload = {
        'sub': db_user.email,
        'name': db_user.email.split('@')[0],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    frontend_token = jwt.encode(jwt_payload, SECRET_KEY, algorithm="HS256")
    return {"token": frontend_token}

@app.get("/")
def home():
    return {"message": "AuthFlowHub API Running"}
