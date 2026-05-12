from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt 
from datetime import datetime, timedelta, timezone
import pandas as pd 
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app=FastAPI(title="Intel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows any website to talk to your API for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL=f"postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PW")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"
engine=create_engine(DB_URL)

#user table

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL
        )
    """))
    conn.commit() 

#------SECURITY------
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")
pwd_context=CryptContext(schemes=["bcrypt"], deprecated= "auto")

#access check
#using Pydantic to tell FastAPI what kind of data to expect
class UserCreate(BaseModel):
    username: str
    password: str
#---SECURITY FUNCTIONS---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
def create_access_token(data: dict):
    to_encode= data.copy()
    expire= datetime.now(timezone.utc) + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def get_current_user(token: str=Depends(oauth2_scheme)):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str= payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    with engine.connect() as conn:
        results=conn.execute(
            text("SELECT username FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if results is None:
            raise credentials_exception
    return username


@app.get("/")
def home():
    return{"message": "Intelligence is Online", "version": "1.0"}
#registration
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    """Allows you to create a new user in the PostgreSQL database."""
    hashed_pw=get_password_hash(user.password)
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO users (username, hashed_password) VALUES (:u, :p)"),
                {"u": user.username, "p": hashed_pw}
            )
            conn.commit()
        return {"message": f"User '{user.username}' succesfully created!"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm =Depends()):
    """The endpoint where you send your username and password to get token."""
    with engine.connect() as conn:
        user_row=conn.execute(
            text("SELECT username, hashed_password FROM users WHERE username= :username"),
            {"username": form_data.username}
        ).fetchone()
    #Check if user exists and password matches hash
    if not user_row or not verify_password(form_data.password, user_row[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user_row[0]})
    return {"access_token": access_token, "token_type": "bearer"}

#DATA ENDPOINTS
@app.get("/news")
def get_news(current_user: str = Depends(get_current_user)):
    try:
        with engine.connect() as conn:
            query=text('SELECT * FROM global_news ORDER BY "pubDate" DESC')
            df=pd.read_sql(query, conn)
        
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/trends")
def get_trends(current_user: str = Depends(get_current_user)):
    try:
        with engine.connect() as conn:
            query=text("SELECT * FROM google_trends ORDER BY date ASC")
            df=pd.read_sql(query, conn)
            # Convert the date column to a string with just YYYY-MM-DD
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        return df.to_dict(orient="records")
    except Exception as e:
        return{"error": str(e)}