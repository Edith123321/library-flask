from app import app
from models import db, Book, Author, Member, Loan, BookAuthor
from datetime import date, timedelta

with app.app_context():
    db.drop_all()
    db.create_all()
    
    # Create authors
    authors = [
        Author(name="J.K. Rowling", birth_date=date(1965, 7, 31)),
        Author(name="George Orwell", birth_date=date(1903, 6, 25)),
        Author(name="Jane Austen", birth_date=date(1775, 12, 16))
    ]
    db.session.add_all(authors)
    
    # Create books
    books = [
        Book(title="Harry Potter", isbn="9780747532743", publication_date=date(1997, 6, 26)),
        Book(title="1984", isbn="9780451524935", publication_date=date(1949, 6, 8)),
        Book(title="Pride and Prejudice", isbn="9780141439518", publication_date=date(1813, 1, 28))
    ]
    db.session.add_all(books)
    
    # Create book-author associations
    book_authors = [
        BookAuthor(book_id=1, author_id=1),
        BookAuthor(book_id=2, author_id=2),
        BookAuthor(book_id=3, author_id=3)
    ]
    db.session.add_all(book_authors)
    
    # Create members
    members = [
        Member(name="Alice Johnson", email="alice@example.com"),
        Member(name="Bob Smith", email="bob@example.com")
    ]
    db.session.add_all(members)
    
    # Create some loans
    loans = [
        Loan(
            book_id=1,
            member_id=1,
            loan_date=date.today() - timedelta(days=10),
            due_date=date.today() + timedelta(days=4)
        ),
        Loan(
            book_id=2,
            member_id=2,
            loan_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9),
            return_date=date.today()
        )
    ]
    db.session.add_all(loans)
    
    db.session.commit()