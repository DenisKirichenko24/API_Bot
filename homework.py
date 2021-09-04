import os
import time
import requests
import telegram
import logging
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w'
)
logger = logging.getLogger(__name__)


bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = ['reviewing', 'approved', 'rejected']


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None and homework_status is None:
        return ('Пришли пустые данные!')
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    logger.info('Получение домашних работ')
    if current_timestamp is None:
        current_timestamp = int(time.time())
    try:
        homework_statuses = requests.get(
            f'{url}',
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params={'from_date': current_timestamp})
        return homework_statuses.json()
    except ValueError as error:
        logging.exception(f'Не верно переданное значение {error}')
        return {}
    except requests.exceptions.RequestException as error:
        logging.exception(f'В запросе ошибка {error}')
        return {}


def send_message(message):
    logger.info('Отправка сообщения')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    logger.info('Бот запущен')
    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            if homeworks.get('homeworks'):
                send_message(parse_homework_status(homeworks.get('homeworks')))
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logging.exception(error_message)
            logger.error(error_message)
            bot.send_message(chat_id=CHAT_ID, text=error_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
