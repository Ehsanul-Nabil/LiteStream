from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_user_by_token

router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)

@router.post("/{video_id}")
def like_video(video_id: int, token: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Token")
        
    video = db.query(models.Video).filter(models.Video.id == video_id).first()

    print("Videos Existed",video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video Not Found")
        
    existing_like = db.query(models.Like).filter(models.Like.user_id == user.id, models.Like.video_id == video_id).first()
    print("Existing Like",existing_like)
    if existing_like is not None:
        db.delete(existing_like)
        print("Delete")
        if video.likes>0:
            video.likes -= 1
        liked = False
    else:
        like = models.Like(user_id=user.id, video_id=video_id)
        db.add(like)
        print("ADD")
        video.likes += 1
        liked = True
    print("Videos Likes",video.likes)
    print("liked : ",liked)
    db.commit()
    return {"likes": video.likes, "liked": liked}

@router.post("/check/{video_id}")
def check_liked(video_id: int, token: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        return {"liked": False}
        
    liked = db.query(models.Like).filter(models.Like.user_id == user.id, models.Like.video_id == video_id).first() is not None
    return {"liked": liked}