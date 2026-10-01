class BookNotFound(Exception):
    def __init__(
        self,
        book_isbn: str,
    ) -> None:
        self.book_isbn = book_isbn


class BookInCurrentLoan(Exception):
    def __init__(self, book_isbn: str) -> None:
        self.book_isbn = book_isbn


class BookNotAvailable(Exception):
    def __init__(self, book_isbn: str) -> None:
        self.book_isbn = book_isbn
