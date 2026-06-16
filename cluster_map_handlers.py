from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_found_locations_by_empire,
    get_total_empires_from_cluster
)
from models import (
    EmpireLocations,
    Mission,
    EmpireMission
)
from i18n import I18N
import json
from locales.locales_names import locations_name, items_name


i18n = I18N("ru")



async def cluster_map_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    caption = i18n.t("render.cluster_map.main_menu")


    keyboard = [
        [
            InlineKeyboardButton(i18n.t("render.cluster_map.buttons.founded_locations"), callback_data="cluster_map_finder_locations")
        ],
        [
            InlineKeyboardButton(i18n.t("render.cluster_map.buttons.empires_list"), callback_data="cluster_map_list_empiries")
        ],
        [
            InlineKeyboardButton(i18n.t("buttons.back"), callback_data="menu_game_handler")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=caption,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def cluster_map_finder_locations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOCATIONS_PER_PAGE = 5

    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    query_data = update.callback_query.data
    page = int(query_data.split("_")[-1]) if query_data.startswith("cluster_map_finder_locations_page_") else 1


    found_locations = EmpireLocations.select().where(EmpireLocations.empire == empire)
    total_locations = len(found_locations)


    start_idx = (page - 1) * LOCATIONS_PER_PAGE
    end_idx = start_idx + LOCATIONS_PER_PAGE
    locations_slice = found_locations[start_idx:end_idx]

    keyboard = []

    for location in locations_slice:
        cb_data = f"location_report_{location.id}"

        keyboard.append([InlineKeyboardButton(f"🔍 {locations_name[location.name]}", callback_data=cb_data)])


    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(i18n.t("buttons.back"), callback_data=f"cluster_map_finder_locations_page_{page - 1}"))
    if end_idx < total_locations:
        pagination_buttons.append(InlineKeyboardButton(i18n.t("buttons.forward"), callback_data=f"cluster_map_finder_locations_page_{page + 1}"))

    if pagination_buttons:
        keyboard.append(pagination_buttons)


    keyboard.append([InlineKeyboardButton(i18n.t("buttons.back"), callback_data="cluster_map_handler")])


    message = i18n.t("render.cluster_map.report_found_locations_title") if keyboard else i18n.t("render.other.not_found_all")

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def location_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    query_data = update.callback_query.data
    location_id = query_data.split("_")[-1]


    location = EmpireLocations.get_or_none(EmpireLocations.id == location_id)

    if not location:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.cluster_map.location_not_found"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(i18n.t("buttons.back"), callback_data="cluster_map_finder_locations")]]),
            parse_mode="HTML"
        )
        return


    mission_type = Mission.get_or_none(Mission.name == "attack_location")
    is_under_attack = (
        mission_type and EmpireMission.select().where(
            (EmpireMission.location == location) &
            (EmpireMission.mission_type == mission_type) &
            (EmpireMission.status == "pending")
        ).exists()
    )

    item_name = items_name.get(location.item_name) or "Нет предмета"

    message_parts = [
        i18n.t("render.cluster_map.report_location.line_01", location_name=location.name),
        i18n.t("render.cluster_map.report_location.line_02", location_wood=location.wood),
        i18n.t("render.cluster_map.report_location.line_03", location_gold=location.gold),
        i18n.t("render.cluster_map.report_location.line_04", location_oil=location.oil),
        i18n.t("render.cluster_map.report_location.line_05", location_diamond=location.diamond),
        i18n.t("render.cluster_map.report_location.line_06", location_monsters=location.monsters),
        i18n.t("render.cluster_map.report_location.line_07", location_item=item_name)
    ]
    report_text = "".join(message_parts)

    if is_under_attack:
        report_text += i18n.t("render.cluster_map.report_location.location_attacked")


    keyboard = []
    if not is_under_attack:
        keyboard.append([InlineKeyboardButton(i18n.t("render.cluster_map.buttons.attack_location"), callback_data=f"cluster_map_location_attack_{location.id}")])
    keyboard.append([InlineKeyboardButton(i18n.t("buttons.back"), callback_data="cluster_map_finder_locations")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=report_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def cluster_map_list_empiries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    PAGE_SIZE = 10

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    empires_from_cluster = get_total_empires_from_cluster(empire)
    total_empires = len(empires_from_cluster)


    total_pages = max((total_empires + PAGE_SIZE - 1) // PAGE_SIZE, 1)


    query_data = update.callback_query.data
    if query_data.startswith("cluster_map_list_page_"):
        page = int(query_data.rsplit('_', 1)[1])
    else:
        page = 0


    page = max(0, min(page, total_pages - 1))


    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    page_empires = empires_from_cluster[start_index:end_index]


    caption = i18n.t("render.cluster_map.report_empires_list_title")
    caption += i18n.t("render.other.page_current", page=page + 1, total_pages=total_pages)

    for empire in page_empires:
        empire_id = empire.empire_id
        empire_name = empire.name
        caption += i18n.t("render.cluster_map.report_empires_line_record", empire_name=empire_name, empire_id=empire_id)


    keyboard = []

    if page > 0:
        keyboard.append([
            InlineKeyboardButton(i18n.t("buttons.page_back"), callback_data=f"cluster_map_list_page_{page - 1}")
        ])

    if page < total_pages - 1:
        keyboard.append([
            InlineKeyboardButton(i18n.t("buttons.page_forward"), callback_data=f"cluster_map_list_page_{page + 1}")
        ])

    keyboard.append([InlineKeyboardButton(i18n.t("buttons.back"), callback_data="cluster_map_handler")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=caption,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
