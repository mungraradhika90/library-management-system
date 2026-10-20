# from library.library import Library

# lib = Library()

# book = lib.add_book(
#     "Python Basics",
#     "John Smith",
#     "9781234567890",
#     3
# )

# # lib.save()

# # print("Data saved successfully!")

# # lib2 = Library()
# # lib2.load()

# # print(lib2.books)

# from library.library import Library

# lib = Library()
# lib.load()

# print("Books:", lib.books)
# print("Members:", lib.members)
# print("Loans:", lib.loans)


# from library.library import Library

# lib = Library()
# lib.load()

# # Register a member
# member = lib.register_member("Rahul Patel", "rahul@gmail.com")
# print("Registered Member:", member)

# # Issue a book
# loan = lib.issue_book(member.member_id, "B001")
# print("Book Issued:", loan)

# # Check available copies
# print("Available Copies:", lib.books["B001"].available_copies)

# # Save updated data
# lib.save()
# print("Data saved successfully!")




from library.library import Library

lib = Library()
lib.load()

# Register a member only if not already registered
if "M001" in lib.members:
    member = lib.members["M001"]
else:
    member = lib.register_member(
        "Rahul Patel", "rahul@gmail.com"
    )

# Issue the book only if it is not already issued
active_loan = None
for loan in lib.loans.values():
    if (loan.member_id == member.member_id
            and loan.book_id == "B001"
            and loan.return_date is None):
        active_loan = loan
        break

if active_loan is None:
    loan = lib.issue_book(member.member_id, "B001")
    print("Book Issued:", loan)
else:
    print("Book is already issued:", active_loan)


# Return the book
fine = lib.return_book("M001", "B001")

print("Fine:", fine)
print(
    "Available Copies:",
    lib.books["B001"].available_copies
)

# Save changes to JSON
lib.save()
print("Return data saved successfully!")


lib.save()


# from datetime import date, timedelta
# from library.models import Loan

# # Book ni due date thi 5 divas pachhi return
# due = date(2026, 11, 3)

# loan = Loan(
#     loan_id="TEST001",
#     book_id="B001",
#     member_id="M001",
#     issue_date=date(2026, 10, 20),
#     due_date=due,
#     return_date=due + timedelta(days=5),
#     fine=0
# )

# fine = loan.calculate_fine()

# print("Days Late:", (loan.return_date - loan.due_date).days)
# print("Fine:", fine)

# from datetime import date, timedelta
# from library.models import Loan

# due = date(2026, 11, 3)

# loan = Loan(
#     loan_id="TEST002",
#     book_id="B001",
#     member_id="M001",
#     issue_date=date(2026, 10, 20),
#     due_date=due,
#     return_date=due + timedelta(days=60),
#     fine=0
# )

# print("Days Late:", 60)
# print("Fine:", loan.calculate_fine())


# from library.library import Library
# from library.exceptions import UnpaidFineError

# lib_test = Library()

# # Add a book and register a member
# book = lib_test.add_book(
#     "Test Book", "Test Author", "TEST-001", 2
# )

# member = lib_test.register_member(
#     "Test Member", "test@example.com"
# )

# # Set unpaid fine above ₹100
# member.unpaid_fine = 150

# try:
#     lib_test.issue_book(member.member_id, book.book_id)
#     print("Test failed: Book was issued!")
# except UnpaidFineError:
#     print("Test passed: Unpaid fine blocks book issue!")


import os
import tempfile
import unittest
from datetime import date, timedelta

from library.library import Library
from library.models import Loan
from library.exceptions import (
    DuplicateError,
    BookNotAvailableError,
    LimitExceededError,
    UnpaidFineError,
    InvalidReturnError,
)


class TestLibraryManagement(unittest.TestCase):

    def setUp(self):
        # Temporary file: original JSON data safe rahe
        self.temp_dir = tempfile.TemporaryDirectory()
        data_file = os.path.join(
            self.temp_dir.name, "test_library.json"
        )
        self.lib = Library(data_file=data_file)

        self.today = date(2026, 1, 1)

        self.book = self.lib.add_book(
            "Python Basics", "John Smith", "ISBN001", 3
        )

        self.member = self.lib.register_member(
            "Rahul Patel", "rahul@example.com"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_search_book(self):
        results = self.lib.search_books("python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Basics")

    def test_duplicate_isbn(self):
        with self.assertRaises(DuplicateError):
            self.lib.add_book(
                "Another Book", "Author", "ISBN001", 1
            )

    def test_duplicate_email(self):
        with self.assertRaises(DuplicateError):
            self.lib.register_member(
                "Another Member", "rahul@example.com"
            )

    def test_issue_book(self):
        loan = self.lib.issue_book(
            self.member.member_id,
            self.book.book_id,
            today=self.today
        )

        self.assertEqual(loan.issue_date, self.today)
        self.assertEqual(
            self.book.available_copies, 2
        )

    def test_return_book_and_fine(self):
        self.lib.issue_book(
            self.member.member_id,
            self.book.book_id,
            today=self.today
        )

        due_date = self.today + timedelta(days=14)
        return_date = due_date + timedelta(days=5)

        fine = self.lib.return_book(
            self.member.member_id,
            self.book.book_id,
            today=return_date
        )

        self.assertEqual(fine, 50)
        self.assertEqual(self.member.unpaid_fine, 50)
        self.assertEqual(self.book.available_copies, 3)

    def test_maximum_fine_500(self):
        due_date = self.today + timedelta(days=14)

        loan = Loan(
            loan_id="TEST001",
            book_id=self.book.book_id,
            member_id=self.member.member_id,
            issue_date=self.today,
            due_date=due_date,
            return_date=due_date + timedelta(days=60),
            fine=0
        )

        self.assertEqual(loan.calculate_fine(), 500)

    def test_unpaid_fine_blocks_issue(self):
        self.member.unpaid_fine = 150

        with self.assertRaises(UnpaidFineError):
            self.lib.issue_book(
                self.member.member_id,
                self.book.book_id,
                today=self.today
            )

    def test_fine_exactly_100_allows_issue(self):
        self.member.unpaid_fine = 100

        loan = self.lib.issue_book(
            self.member.member_id,
            self.book.book_id,
            today=self.today
        )

        self.assertIsNotNone(loan)

    def test_maximum_three_books(self):
        # Member ne tran books issue kariye
        for i in range(3):
            book = self.lib.add_book(
                f"Book {i}", f"Author {i}", f"ISBN{i+2}", 1
            )
            self.lib.issue_book(
                self.member.member_id,
                book.book_id,
                today=self.today
            )

        # Chothi book issue na thavi joie
        extra_book = self.lib.add_book(
            "Book Four", "Author Four", "ISBN005", 1
        )

        with self.assertRaises(LimitExceededError):
            self.lib.issue_book(
                self.member.member_id,
                extra_book.book_id,
                today=self.today
            )

    def test_book_not_available(self):
        # Book ni badhi copies issue kari do
        for i in range(3):
            member = self.lib.register_member(
                f"Member {i}", f"member{i}@example.com"
            )
            self.lib.issue_book(
                member.member_id,
                self.book.book_id,
                today=self.today
            )

        another_member = self.lib.register_member(
            "Fourth Member", "fourth@example.com"
        )

        with self.assertRaises(BookNotAvailableError):
            self.lib.issue_book(
                another_member.member_id,
                self.book.book_id,
                today=self.today
            )

    def test_overdue_loans(self):
        self.lib.issue_book(
            self.member.member_id,
            self.book.book_id,
            today=self.today
        )

        check_date = self.today + timedelta(days=20)
        overdue = self.lib.overdue_loans(today=check_date)

        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0]["days_late"], 6)

    def test_member_history(self):
        self.lib.issue_book(
            self.member.member_id,
            self.book.book_id,
            today=self.today
        )

        history = self.lib.member_history(
            self.member.member_id
        )

        self.assertEqual(len(history), 1)

    def test_invalid_return(self):
        with self.assertRaises(InvalidReturnError):
            self.lib.return_book(
                self.member.member_id,
                self.book.book_id,
                today=self.today
            )

    def test_save_and_load(self):
        self.lib.issue_book(
            self.member.member_id,
            self.book.book_id,
            today=self.today
        )
        self.lib.save()

        # Same temporary JSON file mathi data load kariye
        loaded_lib = Library(data_file=self.lib.data_file)
        loaded_lib.load()

        self.assertIn(self.book.book_id, loaded_lib.books)
        self.assertIn(self.member.member_id, loaded_lib.members)
        self.assertEqual(len(loaded_lib.loans), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
