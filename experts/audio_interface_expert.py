from experts import base


class AudioInterface(base.Expert):
    data_file_name = 'audio_interface'

    def run_in_console(self):
        for q_num, question in enumerate(self.questions):
            answer = input(f'{q_num}. {question} (1: no, 2: probably no, 3: do not know, 4: probably, 5: yes) -> ')
            if answer == '1':
                self.handle_answer(q_num, 0)
            elif answer == '2':
                self.handle_answer(q_num, 1)
            elif answer == '3':
                continue
            elif answer == '4':
                self.handle_answer(q_num, 3)
            elif answer == '5':
                self.handle_answer(q_num, 4)
            else:
                break

        for el in self.outcomes:
            print(el['producer'], el['priori_probability'])

        result = self.get_result()
        print(f"\nResult:\nProducer: {result.get('producer')}\nModel: {result.get('model')}\n")


if __name__ == "__main__":
    sound_card = AudioInterface()
    sound_card.run_in_console()
