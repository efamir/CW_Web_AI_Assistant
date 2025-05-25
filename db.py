import uuid
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary, DateTime
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import bcrypt

Base = declarative_base()


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship('User', back_populates='role')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(63), unique=True, nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)
    token = Column(String(255), unique=True, nullable=True)
    last_output_file_path = Column(String(255), unique=True, nullable=True)

    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = relationship('Role', back_populates='users')

    notes = relationship('Note', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, password_string, role: Role):
        self.username = username
        self.role_id = role.id
        self.last_output_file_path = None
        self.set_password(password_string)
        self.generate_token()

    def generate_token(self):
        self.token = str(uuid.uuid4())

    def set_password(self, password_string: str):
        password_bytes = password_string.encode('utf-8')
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password_bytes, salt)

    def check_password(self, password_string: str) -> bool:
        password_bytes = password_string.encode('utf-8')
        return bcrypt.checkpw(password_bytes, self.hashed_password)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.name if self.role else 'N/A'}')>"


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    text = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='notes')
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return (f"<Note(id={self.id}, user_id={self.user_id}, "
                f"created_at={self.created_at}, text='{self.text[:30]}...')>")


engine = create_engine('sqlite:///aiAssistandDB.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
