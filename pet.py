from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import (
    get_db, create_tables, User, Organization, AnimalReport,
    UserRole, ReportStatus
)
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_admin, get_current_ngo
)
from schemas import (
    UserCreate, UserResponse, OrganizationCreate, OrganizationResponse,
    AnimalReportCreate, AnimalReportResponse, LoginRequest, Token,
    DashboardResponse, StatusUpdate
)
from datetime import datetime, timedelta, timezone
from auth import ACCESS_TOKEN_EXPIRE_MINUTES

# Create FastAPI app
app = FastAPI(title="Pet Care Welfare System", version="1.0.0")

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    # Create default admin user
    db_gen = get_db()
    db = next(db_gen)
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # Ensure password is a clean string
            admin_password = "admin123"
            admin_user = User(
                username="admin",
                email="admin@petcare.com",
                hashed_password=hash_password(admin_password),
                role=UserRole.admin.value
            )
            db.add(admin_user)
            db.commit()
            print("Default admin created: username=admin, password=admin123")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Pet Care Welfare System"}


# Register NGO endpoint
@app.post("/register", response_model=UserResponse)
def register_ngo(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole.ngo.value
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create organization for the user
    new_org = Organization(
        name=f"{user_data.username}'s Organization",
        description="A welfare organization",
        user_id=new_user.id,
        is_verified=False
    )
    db.add(new_org)
    db.commit()
    
    return new_user


# Login endpoint
@app.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# Admin verify NGO endpoint
@app.post("/admin/verify-ngo/{org_id}", response_model=OrganizationResponse)
def verify_ngo(org_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Find organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Verify organization
    org.is_verified = True
    db.commit()
    db.refresh(org)
    
    return org


# Get all organizations (admin only)
@app.get("/admin/organizations", response_model=list[OrganizationResponse])
def get_all_organizations(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    organizations = db.query(Organization).all()
    return organizations


# Create animal report (NGO only)
@app.post("/reports", response_model=AnimalReportResponse)
def create_report(
    report_data: AnimalReportCreate,
    ngo_user: User = Depends(get_current_ngo),
    db: Session = Depends(get_db)
):
    # Get organization for the NGO user
    org = db.query(Organization).filter(Organization.user_id == ngo_user.id).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found for this user"
        )
    
    if not org.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization not verified yet"
        )
    
    # Create report
    new_report = AnimalReport(
        title=report_data.title,
        description=report_data.description,
        location=report_data.location,
        status=ReportStatus.new.value,
        organization_id=org.id
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


# Update report status (NGO only)
@app.patch("/reports/{report_id}/status", response_model=AnimalReportResponse)
def update_report_status(
    report_id: int,
    status_update: StatusUpdate,
    ngo_user: User = Depends(get_current_ngo),
    db: Session = Depends(get_db)
):
    # Get organization
    org = db.query(Organization).filter(Organization.user_id == ngo_user.id).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Find report
    report = db.query(AnimalReport).filter(AnimalReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if report belongs to organization
    if report.organization_id != org.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this report"
        )
    
    # Validate status
    valid_statuses = [ReportStatus.new.value, ReportStatus.in_progress.value, ReportStatus.resolved.value]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    # Update status and updated_at timestamp
    report.status = status_update.status
    report.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)
    
    return report


# Dashboard endpoint - shows reports by status (NGO only)
@app.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(ngo_user: User = Depends(get_current_ngo), db: Session = Depends(get_db)):
    # Get organization
    org = db.query(Organization).filter(Organization.user_id == ngo_user.id).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get reports by status
    new_reports = db.query(AnimalReport).filter(
        and_(
            AnimalReport.organization_id == org.id,
            AnimalReport.status == ReportStatus.new.value
        )
    ).all()
    
    in_progress_reports = db.query(AnimalReport).filter(
        and_(
            AnimalReport.organization_id == org.id,
            AnimalReport.status == ReportStatus.in_progress.value
        )
    ).all()
    
    resolved_reports = db.query(AnimalReport).filter(
        and_(
            AnimalReport.organization_id == org.id,
            AnimalReport.status == ReportStatus.resolved.value
        )
    ).all()
    
    return DashboardResponse(
        new_reports=new_reports,
        in_progress_reports=in_progress_reports,
        resolved_reports=resolved_reports
    )


# Get current user info
@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

