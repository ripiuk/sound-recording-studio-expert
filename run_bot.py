import misc
from bot import ExpertBotHandler
from experts import AudioInterface, Soundproofing

EQUIPMENTS = ({
        'Аудіо інтерфейс': AudioInterface,
        'Шумоізоляція': Soundproofing,
        'Мікрофон': None,
        'Студійні монітори': None,
        'Мікшерський пульт': None
    }, {
        'Audio interface': AudioInterface,
        'Soundproofing': Soundproofing,
        'Microphone': None,
        'Studio monitor': None,
        'Mixing console': None
    })
LIST_OF_ANSWERS = (('Ні', 'Швидше за все - ні', 'Не знаю', 'Швидше за все - так', 'Так'),
                   ('No', 'Probably no', 'Don\'t know', 'Probably', 'Yes'))
START_TEXT = ('Щоб обрати категорію введіть команду: /menu', 'To select a category, enter the command: /menu')
STOP_TEXT = ('_Щоб вийти з данного опитування введіть команду:_ /stop',
             '_To exit this survey, enter the following command:_ /stop')
MENU_TEXT = ('Оберіть звукозаписуюче обладнання', 'Choose a type of sound recording equipment')
HELP_TEXT = (('MusicStudioExpertBot допоможе вам з укомплектуванням домашньої студії звукозапису. '
              'Вам лише необхідно відповісти на поставленні питання.',
              'Щоб обрати категорію введіть команду: /menu',
              'Також данний бот підтримує наступні команди: /start /help /settings',
              '\n\n[GitHub source](https://github.com/ripiuk)'),
             ('MusicStudioExpertBot is a bot, that can help you to provide a home sound recording studio.',
              'To choose a category from menu - use this command: /menu',
              'Also, this bot supports the following commands: /start /help /settings',
              '\n\n[GitHub source](https://github.com/ripiuk)'))
SETTINGS_TEXT = ('Оберіть мову (лише для навігації)',
                 'Here you can choose a language that you prefer (for navigation only)')
NOT_AVAILABLE_TEXT = ('Ви не можете використовувати команди під час опитування.',
                      'All commands are not available during the quiz.')
RESULT_MESSAGE = ('*Результат:*\n\n*Виробник:* {producer}\n*Модель:* {model}\n*Опис:* {description}',
                  '*Result:*\n\n*Producer:* {producer}\n*Model:* {model}\n*Description:* {description}')
NO_TEXT_MESSAGE = ('Я очікую текст або команду', 'I\'m waiting for some text or command')
QUESTION_NUMBER_PREFIX = ('Поточне питання: ', 'Current question: ')
DONE_MESSAGE = ('Готово', 'Done')
LANGUAGES = {'🇺🇦UA': 0, '🇺🇸US': 1}
DEFAULT_LANGUAGE_ID = 0  # UA


def send_question(expert_bot: ExpertBotHandler, last_chat_id: int, question_text: str,
                  question_number: int, number_of_questions: int, current_language_id: int) -> None:
    """Send current question from quiz to user
    """
    keyboard = expert_bot.build_keyboard(LIST_OF_ANSWERS[current_language_id])
    expert_bot.send_message(chat_id=last_chat_id,
                            text=f'{QUESTION_NUMBER_PREFIX[current_language_id]}'
                                 f'({question_number + 1}/{number_of_questions})\n'
                                 f'*{question_text}*\n\n'
                                 f'{STOP_TEXT[current_language_id]}',
                            reply_markup=keyboard)


def main():
    my_token = misc.token
    expert_bot = ExpertBotHandler(my_token)
    chat_language_for_user = dict()  # chat_id: language_id
    current_step_for_user = dict()  # e.g chat_id: {expert_class: expert, current_step: 0}
    new_offset = None

    while True:
        expert_bot.get_updates(new_offset)
        for update in expert_bot.get_updates():
            last_update_id, last_chat_text, last_chat_id = expert_bot.parse_update_message(update)

            if not last_update_id:
                # Update response is empty
                continue

            current_language_id = chat_language_for_user.get(last_chat_id, DEFAULT_LANGUAGE_ID)
            is_current_user_in_quiz = current_step_for_user.get(last_chat_id, dict()).get(
                'current_step') or current_step_for_user.get(last_chat_id, dict()).get('current_step') == 0

            if not last_chat_text:
                # There is no text in this update
                expert_bot.send_message(last_chat_id, NO_TEXT_MESSAGE[current_language_id])

            if is_current_user_in_quiz:
                if last_chat_text in LIST_OF_ANSWERS[current_language_id]:
                    question_number = current_step_for_user[last_chat_id]['current_step']
                    expert_system = current_step_for_user[last_chat_id]['expert_class']
                    number_of_questions = len(expert_system.questions)

                    if last_chat_text == LIST_OF_ANSWERS[current_language_id][0]:
                        # No
                        expert_system.handle_answer(question_number, 0)
                    elif last_chat_text == LIST_OF_ANSWERS[current_language_id][1]:
                        # Probably no
                        expert_system.handle_answer(question_number, 1)
                    elif last_chat_text == LIST_OF_ANSWERS[current_language_id][2]:
                        # Do not know
                        pass
                    elif last_chat_text == LIST_OF_ANSWERS[current_language_id][3]:
                        # Probably
                        expert_system.handle_answer(question_number, 3)
                    elif last_chat_text == LIST_OF_ANSWERS[current_language_id][4]:
                        # Yes
                        expert_system.handle_answer(question_number, 4)

                    question_number += 1

                    if question_number >= number_of_questions:
                        # Send results
                        result = expert_system.get_result()
                        file_id = result.get('image_id')
                        if file_id:
                            expert_bot.send_photo(last_chat_id, file_id, caption='{} {}'.format(
                                result.get('producer'), result.get('model')))
                        expert_bot.send_message(
                            last_chat_id, RESULT_MESSAGE[current_language_id].format(
                                producer=result.get('producer'), model=result.get('model'),
                                description=result.get('description')),
                            reply_markup=expert_bot.remove_keyboards())
                        del current_step_for_user[last_chat_id]
                    else:
                        # Send next question
                        current_step_for_user[last_chat_id]['current_step'] = question_number
                        question_text = expert_system.questions[question_number]

                        send_question(expert_bot, last_chat_id, question_text,
                                      question_number, number_of_questions, current_language_id)

                elif last_chat_text == '/stop':
                    # Stop this quiz
                    del current_step_for_user[last_chat_id]
                    expert_bot.send_message(chat_id=last_chat_id,
                                            text=DONE_MESSAGE[current_language_id],
                                            reply_markup=expert_bot.remove_keyboards())

                elif last_chat_text.startswith('/'):
                    expert_bot.send_message(chat_id=last_chat_id, text=NOT_AVAILABLE_TEXT[current_language_id])
                    expert_system = current_step_for_user[last_chat_id]['expert_class']
                    question_number = current_step_for_user[last_chat_id]['current_step']
                    question_text = expert_system.questions[question_number]
                    number_of_questions = len(expert_system.questions)

                    send_question(expert_bot, last_chat_id, question_text,
                                  question_number, number_of_questions, current_language_id)

            elif last_chat_text == '/start':
                expert_bot.send_message(last_chat_id, START_TEXT[current_language_id],
                                        reply_markup=expert_bot.remove_keyboards())

            elif last_chat_text == '/menu':
                keyboard = expert_bot.build_keyboard(list(EQUIPMENTS[current_language_id].keys()))
                expert_bot.send_message(last_chat_id, MENU_TEXT[current_language_id], reply_markup=keyboard)

            elif last_chat_text == '/help':
                expert_bot.send_message(
                    chat_id=last_chat_id, text='\n'.join(HELP_TEXT[current_language_id]),
                    reply_markup=expert_bot.remove_keyboards())

            elif last_chat_text == '/settings':
                keyboard = expert_bot.build_keyboard(list(LANGUAGES.keys()))
                expert_bot.send_message(last_chat_id, SETTINGS_TEXT[current_language_id], reply_markup=keyboard)

            elif last_chat_text in LANGUAGES:
                chat_language_for_user[last_chat_id] = LANGUAGES.get(last_chat_text, DEFAULT_LANGUAGE_ID)
                expert_bot.send_message(last_chat_id, DONE_MESSAGE[chat_language_for_user[last_chat_id]],
                                        reply_markup=expert_bot.remove_keyboards())

            elif last_chat_text in EQUIPMENTS[current_language_id]:
                chosen_class = EQUIPMENTS[current_language_id][last_chat_text]
                expert_system = chosen_class()
                current_step_for_user[last_chat_id] = dict(expert_class=expert_system, current_step=0)

                # Send first question to user
                number_of_questions = len(expert_system.questions)
                question_number = 0
                question_text = expert_system.questions[question_number]
                send_question(expert_bot, last_chat_id, question_text,
                              question_number, number_of_questions, current_language_id)

            new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
