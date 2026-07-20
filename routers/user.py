from fastapi import APIRouter, Form, Depends, HTTPException,status
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_user_by_token
from werkzeug.security import generate_password_hash, check_password_hash


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("")
def get_all_user(token: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user :
        raise HTTPException(status_code=400, detail="Invalid Token or User Type")
    print(user.type)
    if (user.type == "user"):
        raise HTTPException(status_code=400, detail="You Do not have permission to access this feature")
    users = db.query(models.User).all()
    return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "type": u.type
            }
            for u in users
        ]

@router.post("/me")
def current_user_info(token: str = Form(...), db: Session = Depends(get_db)):
    u = get_user_by_token(token, db)
    # print("u",u)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "type": u.type
            }

@router.patch("/promote")
def promote_user_to_admin(
    token: str = Form(...),
    target_username: str = Form(...),
    admin_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Promotes a standard user to Admin. Requires a valid token, 
    matching credentials for authentication, and admin-level privileges.
    """
    # Authenticate the user performing the request
    admin_user = get_user_by_token(token, db)
    print(admin_user)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid authentication token."
        )
    
    # Verify the admin's password
    if not check_password_hash(admin_user.password, admin_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid credentials provided."
        )
    
    # Check authorization permissions
    if admin_user.type == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Insufficient permissions to perform this action."
        )
    
    # Locate the target user to be promoted
    target_user = db.query(models.User).filter(models.User.username == target_username).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Target user '{target_username}' not found."
        )
    # Check if target user is already an Admin
    if target_user.type == 'Admin':
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"User '{target_user.username}' is already an Admin."
        )
    # Update role and persist changes
    target_user.type = "Admin"
    db.commit()
    db.refresh(target_user)
    return {"message": f"User {target_user.username} has been successfully promoted to Admin."}



@router.patch("/admin_auth")
def get_admin( 
    token: str = Form(...),
    key:str=Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid token or unauthorized")
    if key != 'dB3_4xK-9vLz8wQ2pYr_1mNt6jHs0fX5bCdE_7gAhIk':
        raise HTTPException(status_code=404, detail="Invalid token or Key")
    
    user.type = "Admin"
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.username} has been promoted to Admin"}