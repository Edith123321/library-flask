from flask import Flask, request, jsonify
from models import db, Book, Author, Member, Loan, BookAuthor
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Helper function for error responses
def error_response(message, status_code):
    return jsonify({'error': message}), status_code

# --- BOOK ENDPOINTS ---
@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        books = Book.query.all()
        return jsonify([{
            'id': b.id,
            'title': b.title,
            'isbn': b.isbn,
            'publication_date': b.publication_date.isoformat() if b.publication_date else None,
            'authors': [{'id': a.id, 'name': a.name} for a in b.authors],
            'available': not any(loan.return_date is None for loan in b.loans)
        } for b in books])
    
    if request.method == 'POST':
        data = request.json
        try:
            book = Book(
                title=data['title'],
                isbn=data['isbn'],
                publication_date=datetime.strptime(data['publication_date'], '%Y-%m-%d').date() if 'publication_date' in data else None
            )
            db.session.add(book)
            
            # Add authors if provided
            if 'author_ids' in data:
                for author_id in data['author_ids']:
                    author = Author.query.get(author_id)
                    if author:
                        book.authors.append(author)
            
            db.session.commit()
            return jsonify({
                'id': book.id,
                'title': book.title,
                'isbn': book.isbn
            }), 201
        except IntegrityError:
            return error_response('Book with this ISBN already exists', 400)
        except ValueError as e:
            return error_response(str(e), 400)

@app.route('/books/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def book_detail(id):
    book = Book.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': book.id,
            'title': book.title,
            'isbn': book.isbn,
            'publication_date': book.publication_date.isoformat() if book.publication_date else None,
            'authors': [{'id': a.id, 'name': a.name} for a in book.authors],
            'loans': [{
                'id': l.id,
                'member': l.member.name,
                'loan_date': l.loan_date.isoformat(),
                'due_date': l.due_date.isoformat(),
                'returned': l.return_date is not None
            } for l in book.loans]
        })
    
    if request.method == 'PATCH':
        data = request.json
        if 'title' in data:
            book.title = data['title']
        if 'isbn' in data:
            book.isbn = data['isbn']
        if 'publication_date' in data:
            book.publication_date = datetime.strptime(data['publication_date'], '%Y-%m-%d').date()
        if 'author_ids' in data:
            book.authors = [Author.query.get(aid) for aid in data['author_ids'] if Author.query.get(aid)]
        
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    
    if request.method == 'DELETE':
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})

# --- AUTHOR ENDPOINTS ---
@app.route('/authors', methods=['GET', 'POST'])
def authors():
    if request.method == 'GET':
        authors = Author.query.all()
        return jsonify([{
            'id': a.id,
            'name': a.name,
            'birth_date': a.birth_date.isoformat() if a.birth_date else None,
            'book_count': len(a.books)
        } for a in authors])
    
    if request.method == 'POST':
        data = request.json
        try:
            author = Author(
                name=data['name'],
                birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if 'birth_date' in data else None
            )
            db.session.add(author)
            db.session.commit()
            return jsonify({
                'id': author.id,
                'name': author.name
            }), 201
        except ValueError as e:
            return error_response(str(e), 400)

@app.route('/authors/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def author_detail(id):
    author = Author.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': author.id,
            'name': author.name,
            'birth_date': author.birth_date.isoformat() if author.birth_date else None,
            'books': [{
                'id': b.id,
                'title': b.title,
                'publication_year': b.publication_date.year if b.publication_date else None
            } for b in author.books]
        })
    
    if request.method == 'PATCH':
        data = request.json
        if 'name' in data:
            author.name = data['name']
        if 'birth_date' in data:
            author.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({'message': 'Author updated successfully'})
    
    if request.method == 'DELETE':
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'})

# --- MEMBER ENDPOINTS ---
@app.route('/members', methods=['GET', 'POST'])
def members():
    if request.method == 'GET':
        members = Member.query.all()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'email': m.email,
            'active_loans': len([l for l in m.loans if l.return_date is None])
        } for m in members])
    
    if request.method == 'POST':
        data = request.json
        try:
            member = Member(
                name=data['name'],
                email=data['email']
            )
            db.session.add(member)
            db.session.commit()
            return jsonify({
                'id': member.id,
                'name': member.name
            }), 201
        except IntegrityError:
            return error_response('Member with this email already exists', 400)

@app.route('/members/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def member_detail(id):
    member = Member.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'loans': [{
                'book_id': l.book_id,
                'book_title': l.book.title,
                'loan_date': l.loan_date.isoformat(),
                'due_date': l.due_date.isoformat(),
                'returned': l.return_date is not None
            } for l in member.loans]
        })
    
    if request.method == 'PATCH':
        data = request.json
        if 'name' in data:
            member.name = data['name']
        if 'email' in data:
            member.email = data['email']
        db.session.commit()
        return jsonify({'message': 'Member updated successfully'})
    
    if request.method == 'DELETE':
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'})

# --- LOAN ENDPOINTS ---
@app.route('/loans', methods=['GET', 'POST'])
def loans():
    if request.method == 'GET':
        loans = Loan.query.all()
        return jsonify([{
            'id': l.id,
            'book_id': l.book_id,
            'book_title': l.book.title,
            'member_id': l.member_id,
            'member_name': l.member.name,
            'loan_date': l.loan_date.isoformat(),
            'due_date': l.due_date.isoformat(),
            'return_date': l.return_date.isoformat() if l.return_date else None,
            'status': 'returned' if l.return_date else 'active'
        } for l in loans])
    
    if request.method == 'POST':
        data = request.json
        book = Book.query.get(data['book_id'])
        member = Member.query.get(data['member_id'])
        
        if not book or not member:
            return error_response('Book or member not found', 404)
        
        # Check if book is already on loan
        active_loan = Loan.query.filter_by(book_id=book.id, return_date=None).first()
        if active_loan:
            return error_response('Book is already on loan', 400)
        
        loan_days = data.get('loan_days', 14)
        if loan_days > 30:
            return error_response('Maximum loan period is 30 days', 400)
        
        loan = Loan(
            book_id=book.id,
            member_id=member.id,
            loan_date=datetime.utcnow().date(),
            due_date=(datetime.utcnow() + timedelta(days=loan_days)).date()
        )
        
        db.session.add(loan)
        db.session.commit()
        return jsonify({
            'id': loan.id,
            'book': book.title,
            'member': member.name,
            'due_date': loan.due_date.isoformat()
        }), 201

@app.route('/loans/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def loan_detail(id):
    loan = Loan.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': loan.id,
            'book': {
                'id': loan.book.id,
                'title': loan.book.title,
                'authors': [a.name for a in loan.book.authors]
            },
            'member': {
                'id': loan.member.id,
                'name': loan.member.name
            },
            'loan_date': loan.loan_date.isoformat(),
            'due_date': loan.due_date.isoformat(),
            'return_date': loan.return_date.isoformat() if loan.return_date else None,
            'status': 'returned' if loan.return_date else 'active'
        })
    
    if request.method == 'PATCH':
        data = request.json
        if 'return_date' in data:
            loan.return_date = datetime.strptime(data['return_date'], '%Y-%m-%d').date()
        if 'due_date' in data:
            new_due = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            if (new_due - loan.loan_date).days > 30:
                return error_response('Maximum loan period is 30 days', 400)
            loan.due_date = new_due
        
        db.session.commit()
        return jsonify({'message': 'Loan updated successfully'})
    
    if request.method == 'DELETE':
        db.session.delete(loan)
        db.session.commit()
        return jsonify({'message': 'Loan deleted successfully'})

@app.route('/loans/<int:id>/return', methods=['POST'])
def return_loan(id):
    loan = Loan.query.get_or_404(id)
    if loan.return_date:
        return error_response('Book already returned', 400)
    
    loan.return_date = datetime.utcnow().date()
    db.session.commit()
    return jsonify({
        'id': loan.id,
        'book': loan.book.title,
        'return_date': loan.return_date.isoformat()
    })
@app.route('/')
def home():
    return 'This is the home page of a library management system'

# --- BOOK-AUTHOR ASSOCIATION ENDPOINTS ---
@app.route('/books/<int:book_id>/authors/<int:author_id>', methods=['POST', 'DELETE'])
def book_author_association(book_id, author_id):
    book = Book.query.get_or_404(book_id)
    author = Author.query.get_or_404(author_id)
    
    if request.method == 'POST':
        if author in book.authors:
            return error_response('Author already associated with this book', 400)
        book.authors.append(author)
        db.session.commit()
        return jsonify({'message': 'Author added to book successfully'})
    
    if request.method == 'DELETE':
        if author not in book.authors:
            return error_response('Author not associated with this book', 404)
        book.authors.remove(author)
        db.session.commit()
        return jsonify({'message': 'Author removed from book successfully'})

if __name__ == '__main__':
    app.run(port=5555, debug=True)