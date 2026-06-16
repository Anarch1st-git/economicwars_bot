async def delete_last_message(context, chat_id: int):
    last_message_id = context.user_data.get("last_message")
    if last_message_id:
        try:
            await context.bot.delete_message(chat_id, last_message_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")
