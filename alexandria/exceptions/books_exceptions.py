class BookNotFound(Exception):
    def __init__(self, book_isbn):
        self.book_isbn = book_isbn


class BookInCurrentLoan(Exception):
    def __init__(self, book_isbn):
        self.book_isbn = book_isbn


class BookIdOrIsbnNotFound(Exception): ...


class BookNotAvailable(Exception):
    def __init__(self, book_isbn):
        self.book_isbn = book_isbn
