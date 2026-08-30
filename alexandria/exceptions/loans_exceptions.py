class HasAlreadyLoanWithBook(Exception):
    def __init__(self, loan_id, book_isbn):
        self.loan_id = loan_id
        self.book_isbn = book_isbn


class LateLoans(Exception):
    def __init__(self, loans_id):
        self.loans_id = loans_id


class MaxUserLoans(Exception): ...


class LoanNotFound(Exception):
    def __init__(self, loan_id):
        self.loan_id = loan_id


class LoanAlreadyReturned(Exception):
    def __init__(self, loan_id):
        self.loan_id = loan_id
