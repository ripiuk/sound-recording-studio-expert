import logging
from decimal import Decimal
from random import randrange

import trafaret as t
from trafaret import Dict

from data import load_data
from experts.exceptions import ProbabilityRatesException, OutcomesValidationException, RangeException

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Expert:
    """An abstract base class for the expert system.
    """

    data_file_name = ''         # type: str
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

        if self.data_file_name:
            # Load questions and outcomes from a file
            data = load_data(self.data_file_name)
            self.questions = data.get('questions')
            self.outcomes = data.get('outcomes')

        self.pid = f'{randrange(2**16):04X}'
        self.log = logging.getLogger(f'Expert.{type(self).__name__}.{self.pid}')
        self._check_rate_range()
        self._validate_outcome_dicts()

    def _check_rate_range(self) -> None:
        """The probably_no_rate and probably_rate variables must be in range
        (-rate_gradation; rate_gradation) and can not be ultimate
        """
        if self.probably_no_rate not in range(-self.rate_gradation + 1, 0) \
                or self.probably_rate not in range(1, self.rate_gradation):
            raise ProbabilityRatesException(
                'One of the following variables not in range ({minus_rate_gradation};{rate_gradation}): '
                'probably_no_rate, probably_rate'.format(
                    minus_rate_gradation=-self.rate_gradation, rate_gradation=self.rate_gradation))
        self.log.debug('Probability rate ranges are OK')

    def _validate_outcome_dicts(self) -> None:
        template = Dict({
            t.Key('id'): t.Int,
            t.Key('producer'): t.String,
            t.Key('model'): t.String,
            t.Key('image_id'): t.Or(t.String(allow_blank=True), t.Null),
            t.Key('description'): t.String(allow_blank=True),
            t.Key('priori_probability'): t.Float,
            t.Key('questions_estimation'): Dict({
                t.Key(1): Dict({
                    t.Key('probability_in_presence'): t.Float,
                    t.Key('probability_in_absence'): t.Float,
                }),
            }).allow_extra('*'),
        })

        if not isinstance(self.outcomes, list):
            raise TypeError('The outcomes variable must be a list instance')

        number_of_products = len(self.outcomes)

        for current_product_number, outcome in enumerate(self.outcomes, 1):
            try:
                template.check(outcome)
            except t.DataError as error:
                self.log.error('Validation error occurred: {err_msg}'.format(err_msg=error))
                raise OutcomesValidationException('Validation error occurred: {}'.format(error))
            else:
                self.log.debug('({}/{}) outcome dictionaries checked.'.format(
                    current_product_number, number_of_products))
        self.log.debug('Outcome dictionaries are OK')

    @staticmethod
    def _calculate_answer_no(p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """If user will answer "NO" to some question, we should
           recalculate a posteriori probability for the assumption

        :param p: a posteriori probability of current assumption
        :param p_y: a conditional probability in presence
        :param p_n: a conditional probability in absence
        :return: new value of a posteriori probability calculated using Bayes' theorem
        """
        return ((1 - p_y) * p) / ((1 - p_y) * p + (1 - p_n) * (1 - p))

    def _calculate_answer_probably_no(self, p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """For more information look at the "calculate_answer_no" method documentation
        """
        return p + (p - ((1 - p_y) * p) / ((1 - p_y) * p + (1 - p_n) *
                                           (1 - p))) * self.probably_no_rate / self.rate_gradation

    @staticmethod
    def _calculate_answer_do_not_know(p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """If user will answer "I don't know" we should not make any calculations

        :param p: a posteriori probability of current assumption
        :return: the same input variable
        """
        return p

    def _calculate_answer_probably(self, p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """For more information look at the "calculate_answer_no" method documentation
        """
        return p + ((p_y * p) / (p_y * p + p_n * (1 - p)) - p) * self.probably_rate / self.rate_gradation

    @staticmethod
    def _calculate_answer_yes(p: Decimal, p_y: Decimal, p_n: Decimal) -> Decimal():
        """For more information look at the "calculate_answer_no" method documentation
        """
        return Decimal((p_y * p) / (p_y * p + p_n * (1 - p)))

    @staticmethod
    def _get_probabilities_from_outcome(outcome: dict, question_number: int) -> tuple:
        """Parce an input dictionary for necessary data to make all calculations

        :param outcome: an input data with all the assumptions and additional info
        :param question_number: a number of current question
        :return: a posteriori probability of current assumption,
        a conditional probability in presence and a conditional probability in absence
        """
        p = Decimal(outcome['priori_probability'])
        p_y = Decimal(outcome['questions_estimation'][question_number]['probability_in_presence'])
        p_n = Decimal(outcome['questions_estimation'][question_number]['probability_in_absence'])
        return p, p_y, p_n

    def handle_answer(self, question_number: int, rate: int) -> None:
        """Handle user answer (No, Probably no, Do not know, Probably, Yes)

        :param question_number: a number of question must be in range [0; +∞)
        :param rate: an answer id. No: 0, Probably no: 1, Do not know: 2, Probably: 3, Yes: 4
        """
        question_number += 1
        if rate not in range(5):
            raise RangeException('Rate number is out of range: [0;4]')
        calculation_methods = {0: self._calculate_answer_no, 1: self._calculate_answer_probably_no,
                               2: self._calculate_answer_do_not_know, 3: self._calculate_answer_probably,
                               4: self._calculate_answer_yes}
        calculation_method = calculation_methods[rate]
        self.log.debug(f'Calculation method is "{calculation_method.__name__}"')
        for outcome in self.outcomes:
            p, p_y, p_n = self._get_probabilities_from_outcome(outcome, question_number)
            outcome['priori_probability'] = calculation_method(p, p_y, p_n)
            self.log.debug(f"Model: {outcome['producer']} {outcome['model']}. "
                           f"Probability: {outcome['priori_probability']}")

    def get_result(self) -> dict:
        return max(self.outcomes, key=lambda x: x['priori_probability'])
