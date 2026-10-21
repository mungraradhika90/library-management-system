
from library.library import Library
from library.exceptions import LibraryError

library = Library()
library.load()

while True:
    print("\n===== Library Management =====")
    print("1.Add book")
    print("2.Remove book")
    print("3.List books")
    print("4.Register member")
    print("5.Issue book")
    print("6.Return book")
    print("7.Search books")
    print("8.Overdue report")
    print("9.Member details & history")
    print("10.Pay fine")
    print("0.Exit")

    choice = input("Enter choice: ")

    try:
        if choice == "1":
            title = input("Enter book Title: ")
            author = input("Enter Author Name: ")
            isbn = input("Enter ISBN: ")
            total_copies = int(input("Enter Number of Copies: "))

            library.add_book(title, author, isbn, total_copies)
            print("Book Added Successfully")

        elif choice == "2":
            book_id = input("Enter Book ID: ")
            library.remove_book(book_id)
            print("Book removed successfully")

        elif choice == "3":
            for book in library.books.values():
                print(
                    book.book_id,
                    book.title,
                    book.author,
                    book.available_copies
                )

        elif choice == "4":
            name = input("Enter member name: ")
            email = input("Enter member email: ")

            member = library.register_member(name, email)
            print("Member registered successfully")
            print("Member ID:", member.member_id)

        elif choice == "5":
            member_id = input("Enter member ID: ")
            book_id = input("Enter book ID: ")

            loan = library.issue_book(member_id, book_id)

            print("Book issued successfully!")
            print("Loan ID:", loan.loan_id)
            print("Due date:", loan.due_date)

        elif choice == "6":
            member_id = input("Enter member ID: ")
            book_id = input("Enter book ID: ")

            fine = library.return_book(member_id, book_id)

            print("Book returned successfully!")
            print("Fine:", fine)

        elif choice == "7":
            query = input("Enter book title or author: ")
            books = library.search_books(query)

            if books:
                for book in books:
                    print(book.book_id, book.title, book.author)
            else:
                print("No books found.")

        elif choice == "8":
            loans = library.overdue_loans()

            if loans:
                for loan in loans:
                    print(
                        loan.loan_id,
                        loan.book_id,
                        loan.member_id,
                        loan.due_date
                    )
            else:
                print("No overdue loans.")

        elif choice == "9":
            member_id = input("Enter member ID: ")
            history = library.member_history(member_id)
            print(library.member_history(member_id))

            if history:
                print("Member History:")
                for loan in history:
                    print(loan)
            else:
                print("No history fund for this member.")
        
        elif choice == "10":
            member_id = input("Enter member ID: ")
            amount = float(input("Enter fine amount to pay: "))

            library.pay_fine(member_id, amount)
            print("Fine payment processed.")

        elif choice == "0":
            # library.save()
            print("Data saved. Exit!")
            break

        else:
            print("Invalid choice.")

    except LibraryError as error:
        print("Error:", error)

    except ValueError as error:
        print("Invalid input:", error)
        
    finally:
        library.save()
        
        

