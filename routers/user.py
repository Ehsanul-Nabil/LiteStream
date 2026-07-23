from fastapi import APIRouter, Form, Depends, HTTPException,status,File,UploadFile
from sqlalchemy.orm import Session
import models
import cloudinary.uploader
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
                "type": u.type,
                "is_active":u.is_active
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
            "type": u.type,
            "profile_pic":u.profile_pic,
            "phone":u.phone,
            "address":u.address,
            "createdAt":u.member_since,
            "is_active":u.is_active,
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


@router.patch("/UpdateProfilePic")
def update_profilePic(
    token: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    try:
        # ফাইলটি সরাসরি রিকোয়েস্ট থেকে Cloudinary-তে আপলোড হচ্ছে
        upload_result = cloudinary.uploader.upload(
            file.file, 
            resource_type = "image",
            folder = "Lite_Stream_UserProfilePic"
        )
        image_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")
    user.profile_pic=image_url
    db.commit()
    db.refresh(user)
    return {"message": f"User {user.username} has Changed Profile Pic", "profile_pic": image_url}


@router.patch("/update_password")
def update_password(
    token: str = Form(..., description="Authentication token or username to identify the user."),
    current_password: str = Form(..., description="Enter your current password for verification."),
    new_password: str = Form(..., description="Enter the new password you wish to use."),
    db: Session = Depends(get_db)
):
    # print("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided."
        )
    user = db.query(models.User).filter(models.User.username == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested user account could not be found."
        )
    if not check_password_hash(user.password, current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid credentials provided."
        )
    user.password = generate_password_hash(new_password)
    db.commit()
    return {
        "success": True,
        "message": "Password updated successfully."
    }
    


@router.put("/update_user")
def update_user_info(
    token: str = Form(..., description="Authentication token or username to identify the user."),
    username: str = Form(None,description="Leave blank if you do not want to update your username."),
    email: str = Form(None, description="Leave blank if you do not want to update your email address."),
    phone: str = Form(None, description="Leave blank if you do not want to update your phone number."),
    address: str = Form(None, description="Leave blank if you do not want to update your residential address."),
    db: Session = Depends(get_db)
):
    print(token)
    user = get_user_by_token(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication credentials were not provided."
        )

    if username is not None and username != user.username:
        # ডাটাবেজে অন্য কোনো ইউজারের এই ইউজারনেম আছে কি না তা চেক করা
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken. Please choose another one."
            )
        user.username = username

    if email is not None:
        user.email = email
    if phone is not None:
        user.phone = phone
    if address is not None:
        user.address = address

    db.commit()
    db.refresh(user)
    return {
        "success": True,
        "message": "User information updated successfully",
        "data": {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "address": user.address
        }
    }


@router.patch("/deactive")
def DeactiveUser(
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid authentication token."
    )
    user.is_active=False
    db.commit()
    db.refresh(user)
    return{"is_active":user.is_active}
    



@router.delete("/delete")
def UserDelete(
    token: str = Form(...),
    target_username: str = Form(...),
    admin_password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Delete a user account from the system.
    Requires administrative privileges and password confirmation.
    """
    # Authenticate the requesting administrator
    admin_user = get_user_by_token(token, db)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid authentication token."
        )
    
    # Verify the administrator's password credentials
    if not check_password_hash(admin_user.password, admin_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid credentials provided."
        )
    
    # Enforce role-based access control (RBAC)
    if admin_user.type == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Insufficient permissions to perform this action."
        )
    
    # Retrieve the target user record
    target_user = db.query(models.User).filter(models.User.username == target_username).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Target user '{target_username}' not found."
        )
        
    # Prevent self-termination of the active administrator account
    if admin_user.username == target_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Administrative accounts cannot delete themselves."
        )

    # Execute record removal and persist transaction
    db.delete(target_user)
    db.commit()
    
    return {"message": f"User account '{target_user.username}' has been successfully deleted."}