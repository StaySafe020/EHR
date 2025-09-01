from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Python backend is running"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.SessionLocal)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.SessionLocal)):
    # Input validation
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not user.username or not user.email:
        raise HTTPException(status_code=400, detail="Username and email required")
    db_user = crud.create_user(db, user)
    return db_user

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/patients/", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin", "doctor", "nurse"]))):
    return crud.create_patient(db, patient)

@app.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: int, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin", "doctor", "nurse"]))):
    db_patient = crud.get_patient(db, patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

# List all patients
@app.get("/patients/", response_model=list[schemas.PatientOut])
def list_patients(db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin", "doctor", "nurse"]))):
    patients = db.query(models.Patient).all()
    return patients

# Update patient profile
@app.put("/patients/{patient_id}", response_model=schemas.PatientOut)
def update_patient(patient_id: int, patient: schemas.PatientCreate, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin", "doctor", "nurse"]))):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in patient.dict().items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# Delete patient profile
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin"]))):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_patient)
    db.commit()
    return {"message": "Patient deleted"}

# Password reset endpoints
@app.post("/password-reset/request")
def request_password_reset(email: str, db: Session = Depends(database.SessionLocal)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = auth.generate_password_reset_token(email)
    # Here you would send the token via email/SMS
    return {"reset_token": token}

@app.post("/password-reset/confirm")
def confirm_password_reset(token: str, new_password: str, db: Session = Depends(database.SessionLocal)):
    email = auth.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return {"message": "Password reset successful"}
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Python backend is running"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.SessionLocal)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.SessionLocal)):
    # Input validation
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not user.username or not user.email:
        raise HTTPException(status_code=400, detail="Username and email required")
    db_user = crud.create_user(db, user)
    return db_user

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/patients/", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin", "doctor", "nurse"]))):
    return crud.create_patient(db, patient)

@app.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: int, db: Session = Depends(database.SessionLocal), current_user: models.User = Depends(auth.require_roles(["admin", "doctor", "nurse"]))):
    db_patient = crud.get_patient(db, patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

# Password reset endpoints
@app.post("/password-reset/request")
def request_password_reset(email: str, db: Session = Depends(database.SessionLocal)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = auth.generate_password_reset_token(email)
    # Here you would send the token via email/SMS
    return {"reset_token": token}

@app.post("/password-reset/confirm")
def confirm_password_reset(token: str, new_password: str, db: Session = Depends(database.SessionLocal)):
    email = auth.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return {"message": "Password reset successful"}