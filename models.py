from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime, timedelta

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    books = db.relationship('Book', secondary='book_authors', back_populates='authors')

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    publication_date = db.Column(db.Date)
    authors = db.relationship('Author', secondary='book_authors', back_populates='books')
    loans = db.relationship('Loan', back_populates='book')

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    loans = db.relationship('Loan', back_populates='member')

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    loan_date = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    
    book = db.relationship('Book', back_populates='loans')
    member = db.relationship('Member', back_populates='loans')
    
    @validates('due_date')
    def validate_due_date(self, key, due_date):
        if due_date < datetime.utcnow().date():
            raise ValueError("Due date cannot be in the past")
        if (due_date - datetime.utcnow().date()).days > 30:
            raise ValueError("Maximum loan period is 30 days")
        return due_date