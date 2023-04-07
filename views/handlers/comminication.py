from logging import getLogger

import telebot

from settings import telegram as tele
from utils.users import get_user_full_name_from_id, get_user_ids

logger = getLogger(__name__)


class AnnouncementHandler:
    """Sends an announcement (a message) to all users."""

    MESSAGES_CHOICES = {
        'confirm_sending': '\U00002705 - отправляем',
        'cancel_sending':  '\U0000274c - отменяем',
    }

    def __init__(self):
        self.sender_id = None
        self.announcement_text = None,
        self.user_ids = []
        self.markup = telebot.types.ReplyKeyboardMarkup()

    def _prepare_announcement(self, message):
        self.markup.add(
            telebot.types.InlineKeyboardButton(text=self.MESSAGES_CHOICES['confirm_sending']),
            telebot.types.InlineKeyboardButton(text=self.MESSAGES_CHOICES['cancel_sending']),
        )

        sender_full_name = ' '.join(get_user_full_name_from_id(message.from_user.id))
        self.user_ids.extend(get_user_ids())
        self.announcement_text = f'Отправитель: {sender_full_name}\n' + message.text

        tele.bot.send_message(
            message.from_user.id,
            f'\U0001f44c\U0001f3fb - записал.\n\nТекст\n{self.announcement_text}\n\nОтправляем?',
            reply_markup=self.markup,
        )
        tele.bot.register_next_step_handler(message, self._send_announcement)

    def _send_announcement(self, message):
        if message.text == self.MESSAGES_CHOICES['cancel_sending']:
            tele.bot.send_message(message.chat.id, '\U0000274E - отменяю.', reply_markup=tele.main_markup)
        elif message.text == self.MESSAGES_CHOICES['confirm_sending']:
            tele.bot.send_message(message.chat.id, '\U0001f552 - отправляю.')

            for user_id in self.user_ids:
                try:
                    tele.bot.send_message(user_id, self.announcement_text)
                except telebot.apihelper.ApiTelegramException:
                    logger.exception('Sending announcement message to user failed', extra={'user_id': user_id})
            tele.bot.send_message(
                message.from_user.id,
                '\U00002705 - сообщение отправлено всем сотрудникам!',
                reply_markup=tele.main_markup,
            )
        else:
            tele.bot.send_message(message.chat.id, '\U00002b07\U0000fe0f - выберите действие.')
            tele.bot.register_next_step_handler(message, self._send_announcement)

    def make_announcement(self, message):
        self.sender_id = message.from_user.id
        tele.bot.send_message(
            self.sender_id,
            f'\U0001f4dd - пришли текст сообщения, которое нужно отправить всем сотрудникам.',
        )
        tele.bot.register_next_step_handler(message, self._prepare_announcement)
