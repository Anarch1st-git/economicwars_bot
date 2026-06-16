from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_news_page,
    get_news_total_pages
)

def build_news_keyboard(current_page: int, total_pages: int):
    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"news_page:{current_page - 1}"))
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Предыдущие ➡️", callback_data=f"news_page:{current_page + 1}"))

    return InlineKeyboardMarkup([buttons]) if buttons else None


async def game_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("1")
    page = 1
    if update.callback_query:
        await update.callback_query.answer()
        _, page_str = update.callback_query.data.split(":")
        page = int(page_str)

    news_list = get_news_page(page)
    total_pages = get_news_total_pages()

    if not news_list:
        await update.effective_chat.send_message("Нет новостей.")
        return

    news_text = "\n\n".join(
        [f"🗓 {n.date.strftime('%Y-%m-%d %H:%M')}\n{n.text}" for n in news_list]
    )
    reply_markup = build_news_keyboard(page, total_pages)

    if update.callback_query:
        await update.callback_query.edit_message_text(news_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(news_text, reply_markup=reply_markup)
