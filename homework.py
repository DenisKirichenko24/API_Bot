import os
import time
import requests
import telegram
import logging
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = ['reviewing', 'approved', 'rejected']


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    logging.info('Получение домашних работ')
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        url,
        params=params,
        headers=headers, )
    return homework_statuses.json()


def send_message(message):
    logging.info('Отправка сообщения')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    logging.info('Бот запущен')
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            if homeworks.get('homeworks'):
                send_message(parse_homework_status(homeworks.get('homeworks')))
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
