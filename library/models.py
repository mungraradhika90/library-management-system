from dataclasses import dataclass
from datetime import date

@dataclass
class Book:
    book_id: str
    title: str
    author: str
    isbn: int
    total_copies: int
    available_copies: int
    
    def is_available(self) -> bool:
        return self.available_copies > 0 
    
    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies
        }
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
        
    
@dataclass
class Member:
    member_id: str
    name: str
    email: str
    joined_on: date
    issued_books: list[str]
    unpaid_fine: int
    
    def can_borrow(self) -> bool:
        return len(self.issued_books) < 3
        # return self.issued_book < 3
    
    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "joined_on": self.joined_on.isoformat(),
            "issued_books": self.issued_books,
            "unpaid_fine": self.unpaid_fine
        }
    
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            member_id=data["member_id"],
            name=data["name"],
            email=data["email"],
            joined_on=date.fromisoformat(data["joined_on"]),
            issued_books=data["issued_books"],
            unpaid_fine=data["unpaid_fine"]
        )

    
@dataclass
class Loan:
    loan_id: str
    book_id: str
    member_id: str
    issue_date: date
    due_date: date
    return_date: date | None = None
    fine: int = 0
    
    def is_overdue(self, today: date | None = None) -> bool:
        if today is None:
            today = date.today()
        
        return self.return_date is None and today > self.due_date
    
    def calculate_fine(self, today: date | None = None) -> int:
        if today is None:
            today = date.today()
            
        if self.return_date is not None:
            end_date = self.return_date
        else:
            end_date = today
            
        days_late = max(0,(end_date - self.due_date).days)
        
        return min(days_late * 10 , 500)
    
    def to_dict(self):
        return {
            "loan_id": self.loan_id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": (
                self.return_date.isoformat()
                if self.return_date else None
            ),
            "fine": self.fine
        }

    @classmethod
    def from_dict(cls, data):
        data["issue_date"] = date.fromisoformat(data["issue_date"])
        data["due_date"] = date.fromisoformat(data["due_date"])

        if data["return_date"] is not None:
            data["return_date"] = date.fromisoformat(data["return_date"])

        return cls(**data)
    
# b1 = Book("b001","python","john smith",963147852,3,0)
# print(b1)
# print(b1.is_available())

# m1 = Member("m001","john","john@gmail.com","14/02/2020",2,150)
# print(m1)
# # print(m1.can_borrow())

# l1 = Loan("l001","b001","m001",date(2021,8,15),date(2021,9,15),date(2021,10,20),10)
# print(l1)
# print(l1.is_overdue())
# print(l1.calculate_fine())
    