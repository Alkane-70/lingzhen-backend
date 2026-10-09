from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# 数据库文件保存在 backend 文件夹下，名为 lingzhen.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/lingzhen.db"

# connect_args={"check_same_thread": False} 是SQLite在FastAPI多线程下必须的参数
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DiagnosisRecord(Base):
    """问诊记录表"""
    __tablename__ = "diagnosis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    symptom = Column(String, index=True)
    department = Column(String)
    confidence = Column(Float)
    reason = Column(String)

# 自动创建表
Base.metadata.create_all(bind=engine)