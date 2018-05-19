import json
import logging

import requests

import misc
from experts import AudioInterface, Soundproofing


class ExpertBotHandler:

    def __init__(self, token: str):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.log = logging.getLogger(f'Bot.{type(self).__name__}')

    def get_updates(self, offset: int=None, timeout: int=30) -> list:
        """Make a GET request to get all the updates

        :param offset: Identifier of the first update to be returned.
        Must be greater by one than the highest among the identifiers of previously received updates.
        By default, updates starting with the earliest unconfirmed update are returned.
        :param timeout: Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling.
        Should be positive, short polling should be used for testing purposes only.
        :return: a list of update results
        """
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result = resp.json()['result']
        self.log.debug(f'Got updates: {result}')
        return result

    def send_message(self, chat_id: int or str, text: str,
                     reply_markup: str=None, parse_mode: str='Markdown') -> requests.models.Response():
        """
        :param chat_id: Unique identifier for the target chat or username of the target channel
        :param text: Text of the message to be sent
        :param reply_markup: Additional interface options. A JSON-serialized object for an inline keyboard,
        custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic,
        fixed-width text or inline URLs in your bot's message.
        """
        method = 'sendMessage'
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        if reply_markup:
            params = {**params, 'reply_markup': reply_markup}
        resp = requests.post(self.api_url + method, params)
        self.log.debug(f'Message delivery status: {resp.status_code}')
        return resp

    def get_last_update(self) -> tuple:
        """Get last update and parse a response

        :return: tuple(last_update_id, last_chat_text, last_chat_id)
        """
        get_result = self.get_updates()
        if not get_result:
            return None, None, None
        last_update = get_result[-1]
        return self._parse_update_message(last_update)

    @staticmethod
    def build_keyboard(items: list) -> str:
        """
        :param items: a list of button names
        :return: a JSON-serialized object for a custom reply keyboard
        """
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True, "resize_keyboard": True}
        return json.dumps(reply_markup)

    @staticmethod
    def remove_keyboards() -> str:
        reply_markup = {"remove_keyboard": True}
        return json.dumps(reply_markup)

    @staticmethod
    def _parse_update_message(message: dict) -> tuple:
        last_update_id = message['update_id']
        last_chat_text = message['message']['text']
        last_chat_id = message['message']['chat']['id']
        return last_update_id, last_chat_text, last_chat_id


def main():
    my_token = misc.token
    expert_bot = ExpertBotHandler(my_token)
    equipments = [{
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
    }]
    list_of_answers = [['Ні', 'Швидше за все - ні', 'Не знаю', 'Швидше за все - так', 'Так'],
                       ['No', 'Probably no', 'Don\'t know', 'Probably', 'Yes']]
    start_text = ['Щоб обрати категорію введіть команду: /menu', 'To select a category, enter the command: /menu']
    stop_text = ['_Щоб вийти з данного опитування введіть команду:_ /stop',
                 '_To exit this survey, enter the following command:_ /stop']
    menu_text = ['Оберіть звукозаписуюче обладнання', 'Choose a type of sound recording equipment']
    help_text = [['MusicStudioExpertBot допоможе вам з укомплектуванням домашньої студії звукозапису. '
                  'Вам лише необхідно відповісти на поставленні питання.',
                  'Щоб обрати категорію введіть команду: /menu',
                  'Також данний бот підтримує наступні команди: /start /help /settings',
                  '\n\n[GitHub source](https://github.com/ripiuk)'],
                 ['MusicStudioExpertBot is a bot, that can help you to provide a home sound recording studio.',
                  'To choose a category from menu - use this command: /menu',
                  'Also, this bot supports the following commands: /start /help /settings',
                  '\n\n[GitHub source](https://github.com/ripiuk)']]
    settings_text = ['Оберіть мову (лише для навігації)',
                     'Here you can choose a language that you prefer (for navigation only)']
    question_number_prefix = ['Поточне питання: ', 'Current question: ']
    chat_language = dict()  # chat_id: language_id
    languages = {'🇺🇦UA': 0, '🇺🇸US': 1}
    default_language_id = 0  # UA
    done_message = ['Готово', 'Done']
    new_offset = None

    while True:
        expert_bot.get_updates(new_offset)
        last_update_id, last_chat_text, last_chat_id = expert_bot.get_last_update()
        if not last_update_id:
            # Update response is empty
            continue
        current_language = chat_language.get(last_chat_id, default_language_id)

        if last_chat_text == '/start':
            expert_bot.send_message(last_chat_id, start_text[current_language],
                                    reply_markup=expert_bot.remove_keyboards())

        elif last_chat_text == '/menu':
            keyboard = expert_bot.build_keyboard(list(equipments[current_language].keys()))
            expert_bot.send_message(last_chat_id, menu_text[current_language], reply_markup=keyboard)

        elif last_chat_text == '/help':
            expert_bot.send_message(
                chat_id=last_chat_id, text='\n'.join(help_text[current_language]),
                reply_markup=expert_bot.remove_keyboards())

        elif last_chat_text == '/settings':
            keyboard = expert_bot.build_keyboard(list(languages.keys()))
            expert_bot.send_message(last_chat_id, settings_text[current_language], reply_markup=keyboard)

        elif last_chat_text in languages:
            chat_language[last_chat_id] = languages.get(last_chat_text, default_language_id)
            expert_bot.send_message(last_chat_id, done_message[chat_language[last_chat_id]],
                                    reply_markup=expert_bot.remove_keyboards())

        elif last_chat_text in equipments[current_language]:
            chosen_class = equipments[current_language][last_chat_text]
            expert_system = chosen_class()
            number_of_questions = len(expert_system.questions)
            question_number = 0

            while question_number != number_of_questions:
                # Send a question
                # FIXME: misunderstanding between few users
                keyboard = expert_bot.build_keyboard(list_of_answers[current_language])
                expert_bot.send_message(chat_id=last_chat_id,
                                        text=f'{question_number_prefix[current_language]}'
                                             f'({question_number + 1}/{number_of_questions})\n'
                                             f'*{expert_system.questions[question_number]}*\n\n'
                                             f'{stop_text[current_language]}',
                                        reply_markup=keyboard)

                # Waiting for some response from user
                new_offset = last_update_id + 1
                expert_bot.get_updates(new_offset)
                last_update_id, last_chat_text, last_chat_id = expert_bot.get_last_update()
                if not last_update_id:
                    # Update response is empty
                    continue

                if last_chat_text == list_of_answers[current_language][0]:
                    expert_system.handle_answer(question_number, 0)
                elif last_chat_text == list_of_answers[current_language][1]:
                    expert_system.handle_answer(question_number, 1)
                elif last_chat_text == list_of_answers[current_language][2]:
                    question_number += 1
                    continue
                elif last_chat_text == list_of_answers[current_language][3]:
                    expert_system.handle_answer(question_number, 3)
                elif last_chat_text == list_of_answers[current_language][4]:
                    expert_system.handle_answer(question_number, 4)
                elif last_chat_text == '/stop':
                    break

                if last_chat_text in list_of_answers[current_language]:
                    question_number += 1

            result = expert_system.get_result()
            expert_bot.send_message(
                last_chat_id, f"Result:\nProducer: {result.get('producer')}\nModel: {result.get('model')}\n",
                reply_markup=expert_bot.remove_keyboards())

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
