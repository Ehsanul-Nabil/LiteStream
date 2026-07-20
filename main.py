from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

import models
from database import engine, get_db
from routers import video, comment, like, user




models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LiteStream Backend")

# CORS Setup
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", tags=["Auth"])
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = generate_password_hash(password)
    user = models.User(username=username, email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    return {"message": "User registered Successful"}


@app.post("/login", tags=["Auth"])
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not check_password_hash(user.password, password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": user.username,"user_role":user.type, "token_type": "bearer"}


app.include_router(user.router)
app.include_router(video.router)
app.include_router(comment.router)
app.include_router(like.router)