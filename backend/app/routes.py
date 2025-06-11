from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import models, schemas, auth, database
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import os, shutil
from app.ml_model import analyze_xray

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    return {"message": f"User {user.role} registered"}

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/upload/", response_model=schemas.ReportOut)
def upload_xray(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = analyze_xray(file_path)

    report = models.Report(filename=file.filename, analysis=result, owner_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/reports/", response_model=list[schemas.ReportOut])
def get_reports(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Report).filter(models.Report.owner_id == current_user.id).all()


@router.get("/all-reports/", response_model=list[schemas.ReportOut])
def all_reports(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Doctor access only")
    return db.query(models.Report).all()


@router.post("/comment/{report_id}")
def add_comment(report_id: int, comment: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Doctor access only")
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.doctor_comment = comment
    db.commit()
    return {"message": "Comment added"}

from sqlalchemy import func
from datetime import datetime, timedelta

@router.get("/user-trend/")
def user_trend(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    reports = db.query(models.Report).filter(models.Report.owner_id == current_user.id).all()
    result = [{"filename": r.filename, "analysis": r.analysis} for r in reports]
    return result

@router.get("/report-summary/")
def report_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403)
    count_normal = db.query(models.Report).filter(models.Report.analysis.like("Normal%")).count()
    count_pneumonia = db.query(models.Report).filter(models.Report.analysis.like("Pneumonia%")).count()
    return {"Normal": count_normal, "Pneumonia": count_pneumonia}

@router.get("/weekly-submissions/")
def weekly_submissions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403)

    today = datetime.today()
    last_week = today - timedelta(days=7)
    result = db.query(func.date(models.Report.id), func.count()).filter(
        models.Report.id > 0  # dummy filter for future timestamp use
    ).group_by(func.date(models.Report.id)).all()
    return [{"date": r[0], "count": r[1]} for r in result]
