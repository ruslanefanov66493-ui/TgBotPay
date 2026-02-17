from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config

# Главное меню (Reply)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Тарифы")],
        [KeyboardButton(text="📖 О курсе"), KeyboardButton(text="📱 Мой профиль")],
        [KeyboardButton(text="🆘 Поддержка")]
    ],
    resize_keyboard=True
)

# Клавиатура со списком тарифов (Inline)
def get_tariffs_keyboard():
    builder = InlineKeyboardBuilder()
    for key, tariff in config.TARIFFS.items():
        builder.button(
            text=f"{tariff['name']} – {tariff['price'] // 100} руб.",
            callback_data=f"tariff_{key}"
        )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для подтверждения платежа (оставлена для совместимости)
payment_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment")]
    ]
)