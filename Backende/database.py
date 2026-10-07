import os
import hashlib
import secrets
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "tatkal_sathi.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(120), default="")
    phone = Column(String(20), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String(32), unique=True, index=True, nullable=False)
    pnr = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    train_id = Column(String(20), nullable=True)
    train_name = Column(String(120), nullable=False)
    source = Column(String(80), nullable=False)
    destination = Column(String(80), nullable=False)
    travel_date = Column(String(20), nullable=False)
    class_name = Column(String(10), nullable=False)
    quota = Column(String(20), nullable=False)
    seats_booked = Column(Integer, default=1)
    fare = Column(Float, default=0.0)
    status = Column(String(20), default="CONFIRMED")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "pnr": self.pnr,
            "user_id": self.user_id,
            "train_id": self.train_id,
            "train_name": self.train_name,
            "source": self.source,
            "destination": self.destination,
            "travel_date": self.travel_date,
            "class_name": self.class_name,
            "quota": self.quota,
            "seats_booked": self.seats_booked,
            "fare": self.fare,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AutomationLog(Base):
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    trigger_type = Column(String(60), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="SUCCESS")
    pnr = Column(String(20), nullable=True)
    train_name = Column(String(120), nullable=True)
    latency_ms = Column(Integer, default=0)
    details = Column(Text, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "trigger_type": self.trigger_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status,
            "pnr": self.pnr,
            "train_name": self.train_name,
            "latency_ms": self.latency_ms,
            "details": self.details,
        }


def hash_password(password: str) -> str:
    """Generate salted SHA-256 hash."""
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against salted hash or fallback plain/legacy."""
    if not stored_hash:
        return False
    if ":" not in stored_hash:
        return password == stored_hash
    salt, digest = stored_hash.split(":", 1)
    calculated = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return secrets.compare_digest(calculated, digest)



def get_db():
    """Session context provider."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables and seed default demo accounts."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Check if demo account exists
        demo_email = "demo@tatkalsathi.com"
        demo_user = session.query(User).filter(
            (User.email == demo_email) | (User.username == "demo")
        ).first()

        if not demo_user:
            demo_user = User(
                username="demo",
                email=demo_email,
                password_hash=hash_password("123456"),
                full_name="Demo Traveler",
                phone="9876543210"
            )
            session.add(demo_user)
            session.commit()
            print("[Database] Seeded demo user: demo@tatkalsathi.com / 123456")
    finally:
        session.close()
    return True


def register_user(username: str, email: str, password: str, full_name: str = "", phone: str = ""):
    """Register a new user in the database."""
    session = SessionLocal()
    try:
        username_clean = username.strip()
        email_clean = email.strip().lower()

        if session.query(User).filter(User.username.ilike(username_clean)).first():
            return False, "Username is already taken."

        if session.query(User).filter(User.email.ilike(email_clean)).first():
            return False, "An account with this email already exists."

        new_user = User(
            username=username_clean,
            email=email_clean,
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            phone=phone.strip()
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return True, new_user.to_dict()
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def authenticate_user(identifier: str, password: str):
    """Authenticate user with username OR email."""
    session = SessionLocal()
    try:
        clean_id = identifier.strip()
        user = session.query(User).filter(
            (User.username.ilike(clean_id)) | (User.email.ilike(clean_id))
        ).first()

        if not user:
            return False, "No account found with this username or email."

        if not verify_password(password, user.password_hash):
            return False, "Incorrect password. Please try again."

        return True, user.to_dict()
    finally:
        session.close()


def get_all_users():
    """Retrieve list of registered users."""
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return [u.to_dict() for u in users]
    finally:
        session.close()


def record_booking(booking_data: dict, user_id: int = None):
    """Store booking record."""
    session = SessionLocal()
    try:
        booking = Booking(
            booking_id=booking_data.get("booking_id", f"BKG-{secrets.token_hex(4).upper()}"),
            pnr=booking_data.get("pnr", f"PNR{secrets.randbelow(89999999)+10000000}"),
            user_id=user_id,
            train_id=str(booking_data.get("train_id", "")),
            train_name=booking_data.get("train_name", "Express Train"),
            source=booking_data.get("source", ""),
            destination=booking_data.get("destination", ""),
            travel_date=str(booking_data.get("travel_date", "")),
            class_name=booking_data.get("class_name", "3A"),
            quota=booking_data.get("quota", "Tatkal"),
            seats_booked=int(booking_data.get("seats_booked", 1)),
            fare=float(booking_data.get("fare", 0.0)),
            status=booking_data.get("status", "CONFIRMED")
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking.to_dict()
    except Exception as e:
        session.rollback()
        print(f"[Database] Error recording booking: {e}")
        return None
    finally:
        session.close()


def log_automation_execution(trigger_type: str, status: str, pnr: str = None,
                             train_name: str = None, latency_ms: int = 0, details: str = ""):
    """Store automation execution log."""
    session = SessionLocal()
    try:
        log_entry = AutomationLog(
            trigger_type=trigger_type,
            status=status,
            pnr=pnr,
            train_name=train_name,
            latency_ms=latency_ms,
            details=details
        )
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        return log_entry.to_dict()
    except Exception as e:
        session.rollback()
        print(f"[Database] Error logging automation: {e}")
        return None
    finally:
        session.close()


def get_recent_automation_logs(limit: int = 15):
    """Retrieve recent automation logs."""
    session = SessionLocal()
    try:
        logs = session.query(AutomationLog).order_by(AutomationLog.timestamp.desc()).limit(limit).all()
        return [l.to_dict() for l in logs]
    finally:
        session.close()
