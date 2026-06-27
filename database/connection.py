from sqlmodel import Session, create_engine

from config import get_settings

settings = get_settings()

# 同步引擎,用 psycopg2 驱动(建表 + get_db 用)
engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()