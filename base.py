import logging
from decimal import Decimal

from exceptions import ProbabilityRatesException


class Expert:
    """An abstract base class for the expert system.
    """

    questions = []              # type: list
    outcomes = []               # type: list
    rate_gradation = 5          # type: int
    probably_no_rate = -3       # type: int
    probably_rate = 3           # type: int
    log_name = 'expert'         # type: str

    def __init__(self):
        """Приклад, для кращого розуміння вхідних данних:

        Питання:      1) У вас є температура?
        Припущення:   Грипп 0.01 1,0.9,0.01 2,1,0.01 3,0,0.01

        Ймовірність P=0.01, що будь-яка навмання взята людина хворіє грипом.
        Ймовірність P=0.9, що при симптомах грипу користувач відповість ТАК на питання чи є у нього температура
        Ймовірність P=0.01 того, що він відповість ТАК на данне питання, але при цьому у нього немає Гриппу
        """

        self.log = logging.getLogger(type(self).__name__)
        self._check_rate_range()

    @staticmethod
    def calculate_answer_no(p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """If user will answer "NO" to some question, we should
           recalculate a posteriori probability for the assumption

        :param p: a posteriori probability of current assumption
        :param p_y: a conditional probability in presence
        :param p_n: a conditional probability in absence
        :return: new value of a posteriori probability calculated using Bayes' theorem
        """
        return ((1 - p_y) * p) / ((1 - p_y) * p + (1 - p_n) * (1 - p))

    def calculate_answer_probably_no(self, p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """For more information look at the "calculate_answer_no" method documentation
        """
        return p + (p - ((1 - p_y) * p) / ((1 - p_y) * p + (1 - p_n) *
                                           (1 - p))) * self.probably_no_rate / self.rate_gradation

    @staticmethod
    def calculate_answer_do_not_know(p: Decimal) -> Decimal():
        """If user will answer "I don't know" we should not make any calculations

        :param p: a posteriori probability of current assumption
        :return: the same input variable
        """
        return p

    def calculate_answer_probably(self, p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """For more information look at the "calculate_answer_no" method documentation
        """
        return p + ((p_y * p) / (p_y * p + p_n * (1 - p)) - p) * self.probably_rate / self.rate_gradation

    def _check_rate_range(self):
        """The probably_no_rate and probably_rate variables must be in range
        (-rate_gradation; rate_gradation) and can not be ultimate
        """
        if self.probably_no_rate not in range(-self.rate_gradation + 1, 0) \
                or self.probably_rate not in range(1, self.rate_gradation):
            raise ProbabilityRatesException(
                'One of the following variables not in range ({minus_rate_gradation};{rate_gradation}): '
                'probably_no_rate, probably_rate'.format(
                    minus_rate_gradation=-self.rate_gradation, rate_gradation=self.rate_gradation))

    @staticmethod
    def calculate_answer_yes(p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """For more information look at the "calculate_answer_no" method documentation
        """
        return Decimal((p_y * p) / (p_y * p + p_n * (1 - p)))

    @staticmethod
    def get_probabilities_from_outcome(outcome: dict, question_number: int) -> tuple:
        """Parce an input dictionary for necessary data to make all calculations

        :param outcome: an input data with all the assumptions and additional info
        :param question_number: a number of current question
        :return: a posteriori probability of current assumption,
        a conditional probability in presence and a conditional probability in absence
        """
        # TODO: add a _validate_outcome_dict() method using trafaret
        p = Decimal(outcome['priori_probability'])
        p_y = Decimal(outcome['questions_estimation'][question_number]['probability_in_presence'])
        p_n = Decimal(outcome['questions_estimation'][question_number]['probability_in_absence'])
        return p, p_y, p_n

    def outcomes_validator(self):
        pass
