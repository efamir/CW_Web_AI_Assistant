import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from db import Base, Role as DBRole, User as DBUser
from app import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    session_for_setup: SQLAlchemySession = TestSessionLocal()
    try:
        user_role = session_for_setup.query(DBRole).filter_by(name="user").first()
        if not user_role:
            user_role = DBRole(name="user")
            session_for_setup.add(user_role)

        admin_role = session_for_setup.query(DBRole).filter_by(name="admin").first()
        if not admin_role:
            admin_role = DBRole(name="admin")
            session_for_setup.add(admin_role)

        session_for_setup.commit()
    except Exception as e:
        print(f"Error creating roles in setup_test_db: {e}")
        session_for_setup.rollback()
    finally:
        session_for_setup.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_s():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    import db as main_db_module
    original_session = main_db_module.session
    main_db_module.session = session

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    main_db_module.session = original_session


@pytest.fixture(scope="function")
def test_client(db_s):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def ensure_static_templates_exist():
    templates_dir = os.path.join(PROJECT_ROOT, "static", "templates")
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir, exist_ok=True)

    template_files = ["admin.html", "index.html", "login.html", "notes.html", "register.html", "timers.html"]
    for file_name in template_files:
        path = os.path.join(templates_dir, file_name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"<html><head><title>{file_name}</title></head><body>{file_name} content</body></html>")