class LibraryError(Exception):    # parent / base class
    pass

class BookNotFoundError(LibraryError):  # child class
    pass

class MemberNotFoundError(LibraryError):
    pass

class BookNotAvailableError(LibraryError):
    pass

class LimitExceededError(LibraryError):
    pass

class UnpaidFineError(LibraryError):
    pass

class InvalidReturnError(LibraryError):
    pass

class DuplicateError(LibraryError):
    pass
