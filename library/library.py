from datetime import date, timedelta
from library.models import Book, Member, Loan
from library.storage import save_data, load_data
from library.exceptions import (
    BookNotFoundError,
    MemberNotFoundError,
    BookNotAvailableError,
    LimitExceededError,
    UnpaidFineError,
    InvalidReturnError,
    DuplicateError
)

class Library:
    
    def __init__(self, data_file="library_data.json"):
        self.books = {}
        self.members = {}
        self.loans = {}
        self.data_file = data_file
        
    def generate_id(self , prefix, existing_items):
        number = len(existing_items) + 1
        return f"{prefix}{number:03d}"
    
    def add_book(self, title, author, isbn, total_copies):
        if total_copies <= 0:
            raise ValueError("total copies must be greater than 0")
        
        for book in self.books.values():
            if book.isbn == isbn:
                raise DuplicateError("ISBN already exists")
            
        book_id = self.generate_id("B", self.books)
        
        book = Book(
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            total_copies=total_copies,
            available_copies=total_copies
        )
        
        self.books[book_id] = book
        return book
    
    def remove_book(self, book_id):
        if book_id not in self.books:
            raise BookNotFoundError("book not found")
        
        book = self.books[book_id]
        
        if book.available_copies != book.total_copies:
            raise ValueError("some copies are currently issued")
            
        del self.books[book_id]
        
    def register_member(self, name, email):
        for member in self.members.values():
            if member.email == email:
                raise DuplicateError("Email already exists")
            
        member_id = self.generate_id("M", self.members)
        
        member = Member(
            member_id=member_id,
            name=name,
            email=email,
            joined_on=date.today(),
            issued_books=[],
            unpaid_fine=0
        )
        self.members[member_id] = member
        return member
        
    def issue_book(self, member_id, book_id, today=None):
        if today is None:
            today= date.today()
            
        if member_id not in self.members:
            raise MemberNotFoundError("Member Not Found")
        
        if book_id not in self.books:
            raise BookNotFoundError("Book Not Found")
        
        member = self.members[member_id]
        book = self.books[book_id]
        
        if not book.is_available():
            raise BookNotAvailableError("Book Not Available")
        
        if not member.can_borrow():
            raise LimitExceededError("maximum 3 book allowed")
        
        if member.unpaid_fine > 100:
            raise UnpaidFineError("please pay your fine first")
        
        loan_id = self.generate_id("L", self.loans)
        
        loan = Loan(
            loan_id=loan_id,
            book_id=book_id,
            member_id=member_id,
            issue_date=today,
            due_date=today + timedelta(days=14),
            return_date=None,
            fine=0
        )
        
        self.loans[loan_id] = loan
        book.available_copies -=1
        member.issued_books.append(book_id)
        
        return loan
    
    
    def return_book(self, member_id, book_id, today=None):
        if today is None:
            today = date.today()

        if member_id not in self.members:
            raise MemberNotFoundError("Member not found")

        if book_id not in self.books:
            raise BookNotFoundError("Book not found")

        member = self.members[member_id]
        book = self.books[book_id]

        for loan in self.loans.values():
            if (
                loan.member_id == member_id
                and loan.book_id == book_id
                and loan.return_date is None
            ):
                loan.return_date = today
                fine = loan.calculate_fine(today)
                loan.fine = fine

                member.unpaid_fine += fine
                member.issued_books.remove(book_id)
                book.available_copies += 1

                return fine

        raise InvalidReturnError("No active loan found")

    def pay_fine(self, member_id, amount):
        if member_id not in self.members:
            raise MemberNotFoundError("Member not found")

        member = self.members[member_id]

        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        if amount > member.unpaid_fine:
            raise ValueError("Payment is more than unpaid fine")

        member.unpaid_fine -= amount

        return member.unpaid_fine

    def search_books(self, keyword):
        result = []
    
        for book in self.books.values():
            if (
                keyword.lower() in book.title.lower()
                or keyword.lower() in book.author.lower()
            ):
                result.append(book)

        return result

    def overdue_loans(self, today=None):
        if today is None:
            today = date.today()

        result = []

        for loan in self.loans.values():
            if loan.is_overdue(today):
                days_late = (today - loan.due_date).days
                fine = loan.calculate_fine(today)

                result.append({
                    "loan_id": loan.loan_id,
                    "book_id": loan.book_id,
                    "member_id": loan.member_id,
                    "due_date": loan.due_date,
                    "days_late": days_late,
                    "fine": fine
                })

        return result   

    def member_history(self, member_id):
        if member_id not in self.members:
            raise MemberNotFoundError("Member Not Found")
        
        result = []
        
        for loan in self.loans.values():
            if loan.member_id == member_id:
                result.append(loan)
                
        return result
                
    def save(self):
        data = {
            "books": {
                key: book.to_dict()
                for key, book in self.books.items()
            },
            "members": {
                key: member.to_dict()
                for key, member in self.members.items()
            },
            "loans": {
                key: loan.to_dict()
                for key, loan in self.loans.items()
            }
        }

        save_data(data, self.data_file)      
        
    def load(self):
        data = load_data(self.data_file)

        self.books = {
            key: Book.from_dict(value)
            for key, value in data.get("books", {}).items()
        }

        self.members = {
            key: Member.from_dict(value)
            for key, value in data.get("members", {}).items()
        }

        self.loans = {
            key: Loan.from_dict(value)
            for key, value in data.get("loans", {}).items()
        }  
        
        
        