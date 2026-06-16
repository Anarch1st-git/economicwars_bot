from telegram import Bot
from configs import (
    BOT_TOKEN
)
import asyncio
from loop_runner import run_async_task


bot = Bot(token=BOT_TOKEN)


async def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram-бота"""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}")


def send_message_sync(chat_id, text):
    """Безопасная синхронная отправка сообщения"""
    try:
        run_async_task(send_telegram_message(chat_id, text))
    except Exception as e:
        print(f"❌ Ошибка при запуске async-задачи: {e}")







