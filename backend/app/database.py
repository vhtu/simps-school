"""
Thiết lập kết nối cơ sở dữ liệu với SQLAlchemy.
Hỗ trợ SQLite (mặc định) và MySQL.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL


# === Tạo engine kết nối ===
# check_same_thread=False cần thiết cho SQLite khi dùng với FastAPI (đa luồng)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine_kwargs = {
    "connect_args": connect_args,
    "echo": False,
}

# Tối ưu hóa kết nối PostgreSQL/Supabase trên môi trường Serverless (Vercel)
if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 300,
        "pool_pre_ping": True,  # Tự động kiểm tra và tái sử dụng kết nối còn sống
    })

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)

# Bật foreign key cho SQLite (mặc định SQLite tắt foreign key)
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# === Tạo session factory ===
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# === Lớp cơ sở cho các model ===
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency injection cho FastAPI - tạo và đóng session tự động.
    Sử dụng: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Khởi tạo cơ sở dữ liệu - tạo tất cả các bảng.
    Gọi hàm này khi ứng dụng khởi động.
    """
    # Import tất cả model để SQLAlchemy biết cần tạo bảng nào
    import app.models.user
    import app.models.location
    import app.models.incident_type
    import app.models.incident
    import app.models.status_history
    import app.models.survey

    Base.metadata.create_all(bind=engine)
