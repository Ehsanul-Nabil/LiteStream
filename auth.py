from sqlalchemy.orm import Session
import models

def get_user_by_token(token: str, db: Session):
    return db.query(models.User).filter(models.User.username == token).first()