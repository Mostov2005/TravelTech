from uuid import UUID

from sqlalchemy.orm import Session

from models import User, Role, RefreshSession


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: UUID):
        return self.db.query(User).filter(
            User.id == user_id
        ).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(
            User.email == email
        ).first()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(
            User.username == username
        ).first()


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str):
        return self.db.query(Role).filter(
            Role.name == name
        ).first()

    def create(self, role: Role):
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_all(self):
        return self.db.query(Role).all()


class RefreshSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: RefreshSession):
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_token_hash(self, token_hash: str):
        return self.db.query(RefreshSession).filter(
            RefreshSession.token_hash == token_hash
        ).first()

    def delete(self, session: RefreshSession):
        self.db.delete(session)
        self.db.commit()