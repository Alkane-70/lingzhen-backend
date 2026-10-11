from sqlalchemy import create_engine, Column, Integer, String, Float,DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# 数据库文件保存在 backend 文件夹下，名为 lingzhen.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/lingzhen.db"

# connect_args={"check_same_thread": False} 是SQLite在FastAPI多线程下必须的参数
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class DiagnosisRecord(Base):
    """问诊记录表"""
    __tablename__ = "diagnosis_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)
    symptom = Column(String, index=True)
    department = Column(String)
    confidence = Column(Float)
    reason = Column(String)
    session_id = Column(String, default="default")  # 会话ID，用来关联多轮对话
    severity = Column(String, default="mild")
    created_at = Column(DateTime, default=datetime.datetime.now)
    chat_history = Column(String)

# 自动创建表
Base.metadata.create_all(bind=engine)