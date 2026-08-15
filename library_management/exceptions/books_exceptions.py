class BookNotFound(Exception):
    def __init__(self, book_isbn):
        self.book_isbn = book_isbn


class BookNotAvailable(Exception):
    def __init__(self, book_isbn):
        self.book_isbn = book_isbn
