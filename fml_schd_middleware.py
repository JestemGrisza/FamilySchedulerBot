"""Authorization -- pass messages only from users in User DB"""
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware

from fml_schd_db import user_exist


class AccessMiddleware(BaseMiddleware):

    async def on_process_message(self, message: types.Message, data: dict):
        # # Get current handler and command
        # handler = current_handler.get()
        # command = logging.info(message.get_command())
        if (not user_exist(int(message.from_user.id))) and (message.get_command() not in '/join'):
            await message.answer("Access Denied.\nUse /join to send request for authorization!")
            raise CancelHandler()
