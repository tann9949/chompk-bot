import logging
import time

from telegram.error import NetworkError


def send_message(chat_id, context, message) -> None:
    is_sent: bool = False
    while not is_sent:
        try:
            context.bot.send_message(
                chat_id=chat_id,
                text=message,
            )
            is_sent = True
        except NetworkError as e:
            logging.warning(f"Error sending message. Retrying in 0.5 second...")
            logging.debug(e)
            time.sleep(0.5)
            continue


def send_photo(chat_id, context, img_path, message = "") -> None:
    is_sent: bool = False
    while not is_sent:
        try:
            context.bot.send_photo(
                photo=open(img_path, "rb"),
                chat_id=chat_id,
                caption=message,
            )
            is_sent = True
        except NetworkError as e:
            logging.warning(f"Error sending message. Retrying in 0.5 second...")
            logging.debug(e)
            time.sleep(0.5)
            continue
