from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException, File,Header
from sqlalchemy.orm import Session
import cloudinary.uploader
from auth import get_user_by_token
from pydantic import BaseModel

import models
from database import get_db

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)



class VideoMetadataCreate(BaseModel):
    title: str
    description: str = None
    video_url: str
    public_id: str

@router.post("/videos")
def create_video_metadata(
    payload: VideoMetadataCreate, 
    authorization: str = Header(None), # Extracts Authorization header from request
    db: Session = Depends(get_db)
):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token header")
    
    token = authorization.split(" ")[1]
    
    # Authenticate user
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    try:
        video = models.Video(
            title=payload.title, 
            description=payload.description, 
            filename=payload.video_url,
            uploader_id=user.id
        )
        db.add(video)
        db.commit()
        db.refresh(video)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {
        "message": "Video metadata saved successfully", 
        "id": video.id, 
        "url": payload.video_url
    }


# @router.post("/upload")
# def upload_video(
#     title: str = Form(...), 
#     description: str = Form(...), 
#     token: str = Form(...), 
#     file: UploadFile = File(...), 
#     db: Session = Depends(get_db)
# ):
#     if not title.strip() or not description.strip():
#         raise HTTPException(status_code=400, detail="Title and Description cannot be empty")
    
#     user = get_user_by_token(token, db)
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid token")
        
#     try:
#         # ফাইলটি সরাসরি রিকোয়েস্ট থেকে Cloudinary-তে আপলোড হচ্ছে
#         upload_result = cloudinary.uploader.upload_large(
#             file.file, 
#             resource_type = "video",
#             folder = "lite_tube_videos"
#         )
#         video_url = upload_result.get("secure_url")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")
        
#     # ডাটাবেজে ক্লাউডিনারি URL সেভ করা হচ্ছে
#     video = models.Video(
#         title=title, 
#         description=description, 
#         filename=video_url, 
#         uploader_id=user.id
#     )
#     db.add(video)
#     db.commit()
#     db.refresh(video)
    
#     return {"message": "Video uploaded successfully to Cloudinary", "id": video.id, "url": video_url}


@router.get("")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(models.Video).all()
    return [
        {
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "likes": video.likes,
            "uploader_id": video.uploader.username if video.uploader else "Unknown",
            "filename": video.filename,
            "created_at": video.created_at,
        }
        for video in videos
    ]


@router.get("/{video_id}")
def stream_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video Not Found")
    
    # সরাসরি ক্লাউডিনারি লিংক রিটার্ন করছে
    return {"url": video.filename}


@router.delete("/{video_id}")
def delete_video(video_id: int, token: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Token")
        
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video Not Found")
        
    if video.uploader_id != user.id:
        raise HTTPException(status_code=400, detail="Not the owner")
        
    # সম্পর্কিত লাইক ও কমেন্টস ডিলিট করা
    db.query(models.Like).filter(models.Like.video_id == video_id).delete()
    db.query(models.Comment).filter(models.Comment.video_id == video_id).delete()
        
    # ডাটাবেজ থেকে ভিডিও রেকর্ড রিমুভ করা
    db.delete(video)
    db.commit()
    
    return {"message": "Video and its likes/comments deleted Successfully"}













# from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException, File
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# import os, shutil, uuid
# from auth import get_user_by_token


# import models
# from database import get_db

# router = APIRouter(
#     prefix="/videos",
#     tags=["Videos"]
# )

# UPLOAD_DIR = "./uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# @router.post("/upload")
# def upload_video(title: str = Form(...), description: str = Form(...), token: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
#     if not title.strip() or not description.strip():
#         raise HTTPException(status_code=400, detail="Title and Description cannot be empty")
    
#     user = get_user_by_token(token, db)
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid token")
        
#     filepath = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{file.filename}")
#     with open(filepath, "wb") as f:
#         shutil.copyfileobj(file.file, f)
        
#     video = models.Video(title=title, description=description, filename=filepath, uploader_id=user.id)
#     db.add(video)
#     db.commit()
#     db.refresh(video)
#     return {"message": "Video uploaded successfully", "id": video.id}

# @router.get("")
# def list_videos(db: Session = Depends(get_db)):
#     videos = db.query(models.Video).all()
#     return [
#         {
#             "id": video.id,
#             "title": video.title,
#             "description": video.description,
#             "likes": video.likes,
#             "uploader_id": video.uploader.username if video.uploader else "Unknown"
#         }
#         for video in videos
#     ]

# @router.get("/{video_id}")
# def stream_video(video_id: int, db: Session = Depends(get_db)):
#     video = db.query(models.Video).filter(models.Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=404, detail="Video Not Found")
#     return FileResponse(video.filename, media_type="video/mp4")


# # @router.delete("/{video_id}")
# # def delete_video(video_id: int, token: str = Form(...), db: Session = Depends(get_db)):
# #     user = get_user_by_token(token, db)
# #     if not user:
# #         raise HTTPException(status_code=400, detail="Invalid Token")
        
# #     video = db.query(models.Video).filter(models.Video.id == video_id).first()
# #     if not video:
# #         raise HTTPException(status_code=404, detail="Video Not Found")
        
# #     if video.uploader_id != user.id:
# #         raise HTTPException(status_code=400, detail="Not the owner")
        
# #     try:
# #         os.remove(video.filename)
# #     except FileNotFoundError:
# #         pass
# #     db.delete(video)
# #     db.commit()
# #     return {"message": "Video deleted Successfully"}




# @router.delete("/{video_id}")
# def delete_video(video_id: int, token: str = Form(...), db: Session = Depends(get_db)):
#     user = get_user_by_token(token, db)
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid Token")
        
#     video = db.query(models.Video).filter(models.Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=404, detail="Video Not Found")
        
#     if video.uploader_id != user.id:
#         raise HTTPException(status_code=400, detail="Not the owner")
        
#     # DELETE FROM likes WHERE likes.video_id = 1;
#     db.query(models.Like).filter(models.Like.video_id == video_id).delete()
#     db.query(models.Comment).filter(models.Comment.video_id == video_id).delete()

#     try:
#         os.remove(video.filename)
#     except FileNotFoundError:
#         pass
        
#     # মেইন ভিডিও ডিলিট ও সেভ করা
#     db.delete(video)
#     db.commit()
    
#     return {"message": "Video and its likes/comments deleted Successfully"}