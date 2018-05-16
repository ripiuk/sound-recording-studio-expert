from decimal import Decimal


class SoundCard:
    questions = ['Вам потрібна компактна звукова карта?',
                 'Вам потрібна дешева звукова карта?',
                 'Ви будете записувати більше 2-х інструментів одночачно?']

    outcomes = [
        {
            'id': 1,
            'card_producer': 'Focusrite',
            'card_model': 'Scarlett Solo 2nd Gen',
            'image_path': '',
            'description': "Надійний і доступний аудіоінтерфейс Focusrite Scarlett Solo 2nd Gen стане для вас"
                           "гарним помічником у записуванні музики. Модель має мікрофонний вхід XLR, щоб "
                           "приєднати мікрофон, і другий — TRS, для електрогітари. У розпорядженні користувача "
                           "на передній частині панелі є кнопка ввімкнення фантомного живлення, "
                           "стереовхід на навушники (є можливість прямого моніторингу), керування гучністю. "
                           "На задній частині розташувалися: 2 RCA виходи для приєднання моніторів. "
                           "Компактний корпус з алюмінію і USB-шина дадуть змогу брати пристрій куди завгодно.",
            'priori_probability': 0.5,  # P
            'current_rate': 0,
            'questions_estimation': {
                1: {
                    'probability_in_presence': 0.7,  # Py
                    'probability_in_absence': 0.01  # Pn
                },
                2: {
                    'probability_in_presence': 0.4,
                    'probability_in_absence': 0.1
                },
                3: {
                    'probability_in_presence': 0.9,
                    'probability_in_absence': 0.2
                }
            }
        },
        {
            'id': 2,
            'card_producer': 'Fake',
            'card_model': 'FakeFake',
            'image_path': '',
            'description': "Sheet",
            'priori_probability': 0.5,
            'questions_estimation': {
                1: {
                    'probability_in_presence': 0.4,
                    'probability_in_absence': 0.1
                },
                2: {
                    'probability_in_presence': 0.05,
                    'probability_in_absence': 0.2
                },
                3: {
                    'probability_in_presence': 0.7,
                    'probability_in_absence': 0.1
                }
            }
        }
    ]

    def run(self):
        # при положительном: Pапостериорная = (Py * P) / ( Py * P + Pn * ( 1 – P ) )
        # При отрицательном: P = ((1 - Py) * P) / ((1 - Py) * P + (1 - Pn) * (1 - P))
        # Не знаю: P = P
        # Промежуточный (-5;0): P = P + (P - Pотриц) * h/5  # 5 - градація
        # Промежуточный (0;+5); P = P + (Pполож - P) * h/5

        # Есть ли у вас температура?
        # Грипп 0.01 1,0.9,0.01 2,1,0.01 3,0,0.01
        #
        # Вероятность P=0.01, что любой наугад взятый человек болеет гриппом.
        # Вероятность P=0.9 что он ответит Да на вопрос есть ли у него температура при Гриппе
        # Вероятность P=0.01 того что он ответит Да на этот вопрос но при этом у него нет Гриппа
        for q_num, question in enumerate(self.questions):
            q_num += 1
            answer = input(f'{q_num}. {question} (1: no, 2: probably no, 3: do not know, 4: probably, 5: yes) -> ')
            if answer == '5':
                for outcome in self.outcomes:
                    p = Decimal(outcome['priori_probability'])
                    p_y = Decimal(outcome['questions_estimation'][q_num]['probability_in_presence'])
                    p_n = Decimal(outcome['questions_estimation'][q_num]['probability_in_absence'])
                    outcome['priori_probability'] = (p_y * p)/(p_y * p + p_n * (1 - p))
            elif answer == '1':
                for outcome in self.outcomes:
                    p = Decimal(outcome['priori_probability'])
                    p_y = Decimal(outcome['questions_estimation'][q_num]['probability_in_presence'])
                    p_n = Decimal(outcome['questions_estimation'][q_num]['probability_in_absence'])
                    outcome['priori_probability'] = ((1 - p_y) * p)/((1 - p_y) * p + (1 - p_n) * (1 - p))
            elif answer == '3':
                continue
            elif answer == '2':
                rate = Decimal(-3)
                for outcome in self.outcomes:
                    p = Decimal(outcome['priori_probability'])
                    p_y = Decimal(outcome['questions_estimation'][q_num]['probability_in_presence'])
                    p_n = Decimal(outcome['questions_estimation'][q_num]['probability_in_absence'])
                    outcome['priori_probability'] = p + (p - ((1 - p_y) * p) /
                                                         ((1 - p_y) * p + (1 - p_n) * (1 - p))) * rate / 5
            elif answer == '4':
                rate = Decimal(3)
                for outcome in self.outcomes:
                    p = Decimal(outcome['priori_probability'])
                    p_y = Decimal(outcome['questions_estimation'][q_num]['probability_in_presence'])
                    p_n = Decimal(outcome['questions_estimation'][q_num]['probability_in_absence'])
                    outcome['priori_probability'] = p + ((p_y * p) /
                                                         (p_y * p + p_n * (1 - p)) - p) * rate / 5
            else:
                break

        for el in self.outcomes:
            print(el['card_producer'], el['priori_probability'])


if __name__ == "__main__":
    sound_card = SoundCard()
    sound_card.run()
