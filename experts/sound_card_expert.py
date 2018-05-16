import base


class SoundCard(base.Expert):
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
            'priori_probability': 0.5,
            'current_rate': 0,
            'questions_estimation': {
                1: {
                    'probability_in_presence': 0.7,
                    'probability_in_absence': 0.01
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
        for q_num, question in enumerate(self.questions):
            q_num += 1
            answer = input(f'{q_num}. {question} (1: no, 2: probably no, 3: do not know, 4: probably, 5: yes) -> ')
            if answer == '5':
                for outcome in self.outcomes:
                    p, p_y, p_n = self.get_probabilities_from_outcome(outcome, q_num)
                    outcome['priori_probability'] = self.calculate_answer_yes(p, p_y, p_n)
            elif answer == '1':
                for outcome in self.outcomes:
                    p, p_y, p_n = self.get_probabilities_from_outcome(outcome, q_num)
                    outcome['priori_probability'] = self.calculate_answer_no(p, p_y, p_n)
            elif answer == '3':
                continue
            elif answer == '2':
                for outcome in self.outcomes:
                    p, p_y, p_n = self.get_probabilities_from_outcome(outcome, q_num)
                    outcome['priori_probability'] = self.calculate_answer_probably_no(p, p_y, p_n)
            elif answer == '4':
                for outcome in self.outcomes:
                    p, p_y, p_n = self.get_probabilities_from_outcome(outcome, q_num)
                    outcome['priori_probability'] = self.calculate_answer_probably(p, p_y, p_n)
            else:
                break

        for el in self.outcomes:
            print(el['card_producer'], el['priori_probability'])


if __name__ == "__main__":
    sound_card = SoundCard()
    sound_card.run()
