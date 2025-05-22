import uuid
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(63), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=True)

    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = relationship('Role', back_populates='users')

    notes = relationship('Note', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.name if self.role else 'N/A'}')>"

    def generate_token(self):
        self.token = str(uuid.uuid4())


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship('User', back_populates='role')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    text = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='notes')

    def __repr__(self):
        return f"<Note(id={self.id}, user_id={self.user_id}, text='{self.text[:30]}...')>"


engine = create_engine('sqlite:///aiAssistandDB.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
