from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
# from mlapp.database import Base

from .extensions import dbase as db
from datetime import datetime 
from sqlalchemy.orm import validates
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from typing import List, Optional
from .forms import RegistrationForm, IssueForm

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    issues = db.relationship('Issue', backref='author', lazy=True)

    def __repr__(self):
        return f'<User (id : {self.user_id}, email : {self.email!r}, password : {self.password} )>'

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    def validator():
        return RegistrationForm


class Issue(db.Model):
    
    __tablename__ = 'issues'

    issue_id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String(250), nullable = False)
    issue = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable = False)
    classification_id = db.Column(db.Integer, db.ForeignKey("classifications.classification_id"), nullable = False)

    def as_dict(self):
       return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    def __repr__(self):
        return f'<Issue (issue_id : {self.issue_id}, comment : {self.comment}, issue : {self.issue} \
            , date_created : {self.date_created}, user_id : {self.user_id}, classification_id = {self.user_id})>'
    
    def validator():
            return IssueForm

class Classification(db.Model):
    __tablename__ = 'classifications'

    classification_id = db.Column(db.Integer, primary_key=True)
    classification = db.Column(db.String(50), unique=True, nullable=False)
    issues = db.relationship('Issue', backref='classified', lazy=True)

    def __repr__(self):
        return f'<Classification (classification_id : {self.classification_id}, classification : {self.classification} )>'
    
class Parent(db.Model):
    #  __tablename__ = "parents"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30))
    children = db.relationship("Child", backref='gaurdian')

class Child(db.Model):
    #  __tablename__ = "children"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30))
    gaurdian_id = db.Column(db.Integer, db.ForeignKey('parent.id')) 

class Owner(db.Model):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    fullname: Mapped[Optional[str]]
    pets:  Mapped[List["Pet"]] = relationship("Pet", back_populates='owner')

class Pet(db.Model):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)
    owner: Mapped["Owner"] = relationship("Owner", back_populates='pets')
