import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import Book, User
from app.dependencies import get_current_user, require_admin
from app.core.config import UPLOAD_DIR, MAX_UPLOAD_MB
from app.schemas import BookOut, ReviewIn

router = APIRouter(prefix="/api/books", tags=["Books"])
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def as_out(book: Book):
    return BookOut(
        id=book.id, title=book.title, author=book.author,
        description=book.description, faculty=book.faculty,
        department=book.department, category=book.category,
        status=book.status, rejection_reason=book.rejection_reason,
        original_filename=book.original_filename, file_size=book.file_size,
        uploader_id=book.uploader_id, uploader_name=book.uploader.full_name,
        created_at=book.created_at
    )

@router.post("/upload", response_model=BookOut, status_code=201)
async def upload_book(
    title: str = Form(..., min_length=2, max_length=240),
    author: str | None = Form(None),
    description: str | None = Form(None),
    faculty: str | None = Form(None),
    department: str | None = Form(None),
    category: str | None = Form(None),
    pdf: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not pdf.filename or Path(pdf.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    content = await pdf.read((MAX_UPLOAD_MB * 1024 * 1024) + 1)
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"PDF must be {MAX_UPLOAD_MB} MB or smaller")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF")
    stored = f"{uuid.uuid4().hex}.pdf"
    (UPLOAD_DIR / stored).write_bytes(content)
    book = Book(
        title=title.strip(), author=author, description=description,
        faculty=faculty, department=department, category=category,
        original_filename=Path(pdf.filename).name, stored_filename=stored,
        file_size=len(content), uploader_id=user.id, status="pending"
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return as_out(book)

@router.get("", response_model=list[BookOut])
def list_books(
    search: str | None = Query(None),
    category: str | None = None,
    faculty: str | None = None,
    status: str = "approved",
    skip: int = 0, limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Book).join(User, Book.uploader_id == User.id)
    if user.role not in ("admin", "super_admin"):
        query = query.filter(Book.status == "approved")
    elif status != "all":
        query = query.filter(Book.status == status)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Book.title.ilike(term), Book.author.ilike(term), Book.description.ilike(term)))
    if category:
        query = query.filter(Book.category == category)
    if faculty:
        query = query.filter(Book.faculty == faculty)
    books = query.order_by(Book.created_at.desc()).offset(skip).limit(limit).all()
    return [as_out(book) for book in books]

@router.get("/mine", response_model=list[BookOut])
def my_books(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.uploader_id == user.id).order_by(Book.created_at.desc()).all()
    return [as_out(book) for book in books]

@router.get("/pending", response_model=list[BookOut])
def pending_books(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.status == "pending").order_by(Book.created_at.asc()).all()
    return [as_out(book) for book in books]

@router.patch("/{book_id}/review", response_model=BookOut)
def review_book(book_id: int, data: ReviewIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if data.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be approved or rejected")
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.status = data.status
    book.rejection_reason = data.rejection_reason if data.status == "rejected" else None
    db.commit()
    db.refresh(book)
    return as_out(book)

@router.get("/{book_id}/download")
def download_book(book_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.status != "approved" and user.role not in ("admin", "super_admin") and book.uploader_id != user.id:
        raise HTTPException(status_code=403, detail="This book is not approved")
    path = UPLOAD_DIR / book.stored_filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="PDF file is missing from storage")
    return FileResponse(path, media_type="application/pdf", filename=book.original_filename)

@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if user.role not in ("admin", "super_admin") and book.uploader_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own book")
    path = UPLOAD_DIR / book.stored_filename
    if path.exists():
        path.unlink()
    db.delete(book)
    db.commit()
