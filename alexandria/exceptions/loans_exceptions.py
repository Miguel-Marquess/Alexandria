class HasAlreadyLoanWithBook(Exception):
    def __init__(self, loan_id: int, book_isbn: str) -> None:
        self.loan_id = loan_id
        self.book_isbn = book_isbn


class LateLoans(Exception):
    def __init__(self, loans_id: list[int]) -> None:
        self.loans_id = loans_id


class MaxUserLoans(Exception): ...


class LoanNotFound(Exception):
    def __init__(self, loan_id: int) -> None:
        self.loan_id = loan_id


class LoanAlreadyReturned(Exception):
    def __init__(self, loan_id: int) -> None:
        self.loan_id = loan_id
