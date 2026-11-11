from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Book
from app.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Administration"])

@router.get("/users")
def users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [{
        "id": u.id, "full_name": u.full_name, "email": u.email,
        "role": u.role, "department": u.department,
        "is_active": u.is_active, "created_at": u.created_at
    } for u in db.query(User).order_by(User.created_at.desc()).all()]

@router.patch("/users/{user_id}/status")
def set_user_status(user_id: int, is_active: bool, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot disable your own account")
    target.is_active = is_active
    db.commit()
    return {"message": "User status updated", "user_id": target.id, "is_active": target.is_active}

@router.get("/stats")
def stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "users": db.query(User).count(),
        "students": db.query(User).filter(User.role == "student").count(),
        "teachers": db.query(User).filter(User.role == "teacher").count(),
        "books": db.query(Book).count(),
        "approved_books": db.query(Book).filter(Book.status == "approved").count(),
        "pending_books": db.query(Book).filter(Book.status == "pending").count(),
        "rejected_books": db.query(Book).filter(Book.status == "rejected").count(),
    }
