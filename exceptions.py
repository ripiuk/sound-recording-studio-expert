class ProbabilityRatesException(Exception):
    def __init__(self, message):
        super().__init__(message)


class OutcomesValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class RangeException(Exception):
    def __init__(self, message):
        super().__init__(message)
