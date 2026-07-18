from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from locales import get_text


def language_keyboard():
    """Инлайн-клавиатура выбора языка."""
    buttons = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard(lang, is_admin=False):
    """Постоянное reply-меню внизу экрана."""
    buttons = [
        [
            KeyboardButton(text=get_text(lang, "btn_donate")),
            KeyboardButton(text=get_text(lang, "btn_stats")),
        ],
        [
            KeyboardButton(text=get_text(lang, "btn_profile")),
            KeyboardButton(text=get_text(lang, "btn_language")),
        ],
        [
            KeyboardButton(text=get_text(lang, "btn_help")),
            KeyboardButton(text=get_text(lang, "btn_contact")),
        ],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text=get_text(lang, "btn_admin"))])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def amounts_keyboard(lang):
    """Инлайн-клавиатура выбора суммы доната."""
    buttons = [
        [
            InlineKeyboardButton(text="15⭐️", callback_data="donate:amt:15"),
            InlineKeyboardButton(text="50⭐️", callback_data="donate:amt:50"),
            InlineKeyboardButton(text="100⭐️", callback_data="donate:amt:100"),
        ],
        [
            InlineKeyboardButton(text="250⭐️", callback_data="donate:amt:250"),
            InlineKeyboardButton(text="500⭐️", callback_data="donate:amt:500"),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_custom_amount"),
                callback_data="donate:custom",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_back"),
                callback_data="menu:main",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_amounts_keyboard(lang):
    """Кнопка «Назад» на шаге ввода своей суммы."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_back"),
                callback_data="donate:open",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def comment_keyboard(lang):
    """Инлайн-клавиатура шага с комментарием к донату."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_write_comment"),
                callback_data="comment:write",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_skip"),
                callback_data="comment:skip",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_back"),
                callback_data="donate:open",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_comment_keyboard(lang):
    """Кнопка «Назад» на шаге ввода текста комментария."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_back"),
                callback_data="comment:ask",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def request_refund_keyboard(lang):
    """Кнопка запроса возврата в профиле."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_request_refund"),
                callback_data="refund:request",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def refund_confirm_keyboard(lang, donation_id):
    """Подтверждение возврата доната."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_refund_yes"),
                callback_data="refund:yes:" + str(donation_id),
            ),
            InlineKeyboardButton(
                text=get_text(lang, "btn_refund_no"),
                callback_data="refund:no",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_refund_keyboard(lang, donation_id):
    """Кнопка возврата доната в уведомлении для админа."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_refund_donation"),
                callback_data="admin_refund:" + str(donation_id),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def contact_admin_notify_keyboard(lang, user_id):
    """Кнопки Ответить/Заблокировать под уведомлением админа о новом сообщении."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "contact_btn_reply"),
                callback_data="contact:reply:" + str(user_id),
            ),
            InlineKeyboardButton(
                text=get_text(lang, "contact_btn_block"),
                callback_data="contact:block:" + str(user_id),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def contact_user_cancel_keyboard(lang):
    """Кнопка отмены на шаге ввода сообщения пользователем."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "contact_cancel"),
                callback_data="contact:cancel",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def contact_reply_cancel_keyboard(lang):
    """Кнопка отмены на шаге ввода ответа админом."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "contact_cancel"),
                callback_data="contact:reply_cancel",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_panel_keyboard(lang):
    """Главное меню админ-панели."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_stats"),
                callback_data="adm:stats",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_goal"),
                callback_data="adm:goal",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_donations"),
                callback_data="adm:donations:0",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_search"),
                callback_data="adm:search",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_broadcast"),
                callback_data="adm:broadcast",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_export"),
                callback_data="adm:export",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗄 Бэкап / восстановление",
                callback_data="adm:backup_menu",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_close"),
                callback_data="adm:close",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_backup_keyboard():
    """Меню бэкапа и восстановления базы (только для владельца)."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📦 Создать бэкап", callback_data="adm:backup_now"
            ),
        ],
        [
            InlineKeyboardButton(
                text="♻️ Восстановить", callback_data="adm:restore_start"
            ),
        ],
        [
            InlineKeyboardButton(text="« Назад", callback_data="adm:home"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_restore_confirm_keyboard():
    """Подтверждение восстановления базы из файла."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Да, восстановить",
                callback_data="adm:restore_confirm",
            ),
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="adm:restore_cancel"
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_back_keyboard(lang):
    """Кнопка возврата в главное меню админ-панели."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_home"),
                callback_data="adm:home",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_goal_keyboard(lang):
    """Меню управления целью сбора."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_set_goal"),
                callback_data="adm:goal:set",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_reset_goal"),
                callback_data="adm:goal:reset",
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_home"),
                callback_data="adm:home",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_donations_keyboard(lang, donations, page, total_pages):
    """Список донатов с пагинацией."""
    buttons = []
    for donation in donations:
        if donation["refunded"] == 1:
            mark = "↩️"
        else:
            mark = "✅"
        label = (
            mark
            + " #"
            + str(donation["id"])
            + " — "
            + str(donation["amount"])
            + "⭐️"
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data="adm:don:" + str(donation["id"])
                    + ":" + str(page),
                )
            ]
        )

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="◀️", callback_data="adm:donations:" + str(page - 1)
            )
        )
    if total_pages > 0:
        nav_row.append(
            InlineKeyboardButton(
                text=str(page + 1) + "/" + str(total_pages),
                callback_data="adm:noop",
            )
        )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="▶️", callback_data="adm:donations:" + str(page + 1)
            )
        )
    if len(nav_row) > 0:
        buttons.append(nav_row)

    buttons.append(
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_home"),
                callback_data="adm:home",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_donation_detail_keyboard(lang, donation_id, refunded, page):
    """Кнопки для одного доната: возврат и назад к списку."""
    buttons = []
    if refunded == 0:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text(lang, "adm_btn_refund_donation"),
                    callback_data="adm:refund:" + str(donation_id)
                    + ":" + str(page),
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_to_list"),
                callback_data="adm:donations:" + str(page),
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_broadcast_confirm_keyboard(lang):
    """Подтверждение рассылки."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_send"),
                callback_data="adm:bc:send",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_cancel"),
                callback_data="adm:home",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
