from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

import models
from database import engine, get_db
from routers import video, comment, like, user
import cloudinary
from typing import Annotated



models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LiteStream Backend")

# CORS Setup
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
   " https://litestream-five.vercel.app/",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cloudinary Configuration ---
cloudinary.config( 
    cloud_name = "dwlugbeiy", 
    api_key = "128434712479645", 
    api_secret = "asyH0JzgzXtOlwNaQE1DRAxYG-8",
    secure = True
)


from typing import Annotated
from fastapi import Form, Depends, HTTPException
from sqlalchemy.orm import Session


@app.post("/register", tags=["Auth"])
def register(
    username: Annotated[str, Form(..., examples=["Name"])],
    email: Annotated[str, Form(..., examples=["Name@gmail.com"])],
    password: Annotated[str, Form(..., examples=[""])],
    phone: Annotated[str, Form(examples=[""])] = "Not set",
    address: Annotated[str, Form(examples=[""])] = "Not set",
    db: Session = Depends(get_db)
):
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = generate_password_hash(password)
    user = models.User(
        username=username, 
        email=email, 
        password=hashed_pw,
        phone=phone,
        address=address
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered Successful"}



@app.post("/login", tags=["Auth"])
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not check_password_hash(user.password, password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return {"access_token": user.username,"user_role":user.type,"profile_pic":user.profile_pic,"is_active":user.is_active, "token_type": "bearer"}


app.include_router(user.router)
app.include_router(video.router)
app.include_router(comment.router)
app.include_router(like.router)