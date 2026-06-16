from telegram import LabeledPrice, PreCheckoutQuery, Update
from telegram.ext import Application, CommandHandler, MessageHandler, PreCheckoutQueryHandler, CallbackQueryHandler, CallbackContext, filters, ConversationHandler
from conf_payments import (

    TEST_PROVIDER_TOKEN,

    CURRENCY
)
from handlers import (
    get_user_by_chat_id
)
from datetime import datetime, timedelta


BUYING = 1

PAYMENT_OPTIONS = {
    "buy_subscribe_7": {"days": 7, "price": 69000, "label": "Подписка на 7 дней"},
    "buy_subscribe_30": {"days": 30, "price": 199900, "label": "Подписка на 30 дней"},
    "buy_subscribe_180": {"days": 180, "price": 799000, "label": "Подписка на 180 дней"},
    "buy_subscribe_360": {"days": 360, "price": 1299000, "label": "Подписка на 360 дней"},


    "buy_top_up_balance_100": {"type": "balance", "amount": 10000, "label": "Пополнение баланса на 100 руб"},
    "buy_top_up_balance_500": {"type": "balance", "amount": 50000, "label": "Пополнение баланса на 500 руб"},
    "buy_top_up_balance_1000": {"type": "balance", "amount": 100000, "label": "Пополнение баланса на 1000 руб"},
    "buy_top_up_balance_5000": {"type": "balance", "amount": 500000, "label": "Пополнение баланса на 5000 руб"}
}

async def buy_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data
    print(data)

    option = PAYMENT_OPTIONS.get(data)
    if not option:
        await query.answer(text="Неизвестный тип платежа.", show_alert=True)
        return ConversationHandler.END

    await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    await query.answer()

    label = option["label"]
    amount = option["price"] if option["type"] == "subscription" else option["amount"]
    value = f"{amount / 100:.2f}"

    prices = [LabeledPrice(label=label, amount=amount)]
    provider_data_dynamic = {
        "receipt": {
            "items": [
                {
                    "description": label,
                    "quantity": "1.00",
                    "amount": {
                        "value": value,
                        "currency": CURRENCY
                    },
                    "vat_code": 1
                }
            ]
        }
    }


    context.user_data["payment_type"] = option["type"]
    context.user_data["payment_value"] = option.get("days") or (amount // 100)

    await context.bot.send_invoice(
        chat_id=chat_id,
        title=label,
        description=label,
        payload=data,
        provider_token=TEST_PROVIDER_TOKEN,
        currency=CURRENCY,
        prices=prices,
        need_phone_number=True,
        send_phone_number_to_provider=True,
        provider_data=provider_data_dynamic
    )

    return BUYING


async def pre_checkout(update: Update, context: CallbackContext) -> None:
    try:
        query = update.pre_checkout_query
        await query.answer(ok=True)
    except Exception as e:
        print(f"Ошибка при обработке PreCheckoutQuery: {e}")


async def successful_payment(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    user = get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text("Пользователь не найден.")
        return ConversationHandler.END

    payment_type = context.user_data.get("payment_type")
    value = context.user_data.get("payment_value")

    if payment_type == "subscription":
        user.subscription_active = True
        user.subscription_end = datetime.now() + timedelta(days=value)
        await update.message.reply_text(
            f"Подписка активирована до {user.subscription_end.strftime('%Y-%m-%d %H:%M:%S')}."
        )
    elif payment_type == "balance":
        user.balance += value
        await update.message.reply_text(
            f"Баланс пополнен на {value} руб. Текущий баланс: {user.balance} руб."
        )
    else:
        await update.message.reply_text("Неизвестный тип платежа.")
        return ConversationHandler.END

    user.save()
    return ConversationHandler.END


async def unsuccessful_payment(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Не удалось выполнить платеж!")
    return ConversationHandler.END


unified_payment_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(buy_handler, pattern="^(buy_subscribe_|buy_top_up_balance_)")
    ],
    states={
        BUYING: [MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)]
    },
    fallbacks=[MessageHandler(filters.ALL, unsuccessful_payment)],
)
