from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_user_by_token


router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.get("/{video_id}")
def get_comments(video_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.video_id == video_id).all()

    return [
        {
            "id": c.id,
            "user": c.user.username if c.user else "Anonymous",
            "content": c.content,
            "timestamp": c.timestamp.strftime("%Y-%m-%d %H:%M"),
        }
        for c in comments
    ]

@router.post("/{video_id}")
def add_comment(video_id: int, token: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Token")
    if not content.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
        
    comment = models.Comment(video_id=video_id, user_id=user.id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "user": user.username,
        "content": comment.content,
        "timestamp": comment.timestamp.strftime('%Y-%m-%d %H:%M')
    }