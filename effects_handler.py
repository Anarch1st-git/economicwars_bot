from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_active_empire_busters,
    get_completed_empire_researches,
    get_empire_items
)
from i18n import I18N
from datetime import datetime
from locales.locales_names import buster_name, buster_description, items_name, items_category


i18n = I18N("ru")



async def empire_effects_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    TECH_EFFECTS = {
        "tech_time_attack_speed_up": "🔺 Миссии атаки: <b>+3%</b> к скорости",
        "tech_time_espionage_speed_up": "🕵️‍♂️ Шпионаж: <b>+3%</b> к скорости",
        "tech_time_exploration_speed_up": "🌍 Исследование: <b>+3%</b> к скорости",
        "tech_attack_action_up": "⚔️ Атака: <b>+5%</b> к эффективности",
        "tech_defence_action_up": "🛡️ Защита: <b>+5%</b> к эффективности",
        "tech_espionage_action_up": "🕶️ Шпионаж: <b>+10%</b> к эффективности",
        "tech_antiespionage_action_up": "🛡️ Антишпионаж: <b>+10%</b> к эффективности",
        "tech_explore_find_up": "🔎 Поиск локаций: <b>+15%</b> к находкам",
        "tech_safety_exp_units_up": "🧭 Безопасность исследователей: <b>+10%</b> к выживаемости",
    }

    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    message = f"🎖️ <b>Текущие эффекты империи:</b>\n\n"

    effects = []


    if user.subscription_status and user.subscription_end and user.subscription_end > datetime.now():
        effects.append("🔥 <b>Подписка активна:</b>")
        effects.append("• Неограниченное количество строек и исследований")
        effects.append("• <b>+15%</b> к добыче ресурсов")
        effects.append("• <b>+15%</b> к изучению технологий")
        effects.append("• <b>+10%</b> к скорости миссий")
        effects.append("• <b>+25%</b> к базовой энергии")
        effects.append("• <b>-3%</b> к содержанию юнитов")
        effects.append("• <b>-1.5%</b> к потреблению энергии зданиями и <b>+5%</b> к её добыче")
        effects.append("")


    busters = get_active_empire_busters(empire)
    if busters:
        effects.append("⚡ <b>Активные бустеры:</b>")
        for eb in busters:
            b = eb.buster
            effects.append(f"• {buster_name[b.name]}: {buster_description[b.description]}")
        effects.append("")


    researches = get_completed_empire_researches(empire)
    tech_effects = []

    for r in researches:
        tech_type = r.research.research_type
        if tech_type in TECH_EFFECTS:
            tech_effects.append(f"• {TECH_EFFECTS[tech_type]}")

    if tech_effects:
        effects.append("🧪 <b>Технологии:</b>")
        effects.extend(tech_effects)
        effects.append("")


    items = get_empire_items(empire)
    if items:
        effects.append("🎒 <b>Предметы:</b>")
        for ei in items:
            item = ei.item
            effects.append(f"• {items_name[item.name]} ({items_category[item.category]}): +{item.value}")
        effects.append("")


    if not effects:
        message += "Нет активных эффектов."
    else:
        message += "\n".join(effects)


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
