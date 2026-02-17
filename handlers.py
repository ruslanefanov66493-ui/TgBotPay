import logging
import uuid
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import config
from database import add_user, get_user, activate_subscription, save_payment, update_payment_status, check_subscription
from keyboards import main_menu, get_tariffs_keyboard, payment_keyboard

router = Router()

class PaymentStates(StatesGroup):
    waiting_for_payment = State()

# ========== СТАРТ ==========
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    add_user(user.id, user.username, user.full_name)
    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        "🌱 Я помогу тебе и твоей семье лучше понимать друг друга.\n"
        "Курс **«Развитие Эмоционального Интеллекта для всей семьи»** — это 6 эмоций, 6 шагов к гармонии в вашем доме.\n\n"
        "Выбери раздел в меню 👇",
        reply_markup=main_menu
    )

# ========== О КУРСЕ ==========
@router.message(F.text == "📖 О курсе")
async def course_info(message: Message):
    text = (
        "🌟 **Курс «Развитие Эмоционального Интеллекта для всей семьи»**\n"
        "6 эмоций = 6 шагов к гармонии в вашем доме 🏡\n\n"
        "❓ **УЗНАЁТЕ СЕБЯ?**\n"
        "• Ребёнок обижается и замыкается — вы не знаете, как подступиться\n"
        "• Дочка боится темноты, а сын — отвечать у доски — уговоры не помогают\n"
        "• Подросток взрывается гневом, хлопает дверями — вы чувствуете бессилие\n"
        "• В доме всё «нормально», но не хватает тепла, лёгкости, общих радостей\n\n"
        "Это не про «плохое воспитание». Это про то, что эмоциями никто не учил управлять. Ни вас. Ни ваших детей.\n\n"
        "🎯 **ЧТО ДАСТ КУРС**\n"
        "Мы не будем читать лекции. Мы проживём каждую эмоцию вместе — через игры, мультфильмы, арт-терапию, разборы и домашние задания.\n\n"
        "🗓 **ФОРМАТ**\n"
        "• 6 очных занятий (глубокая проработка каждой эмоции)\n"
        "• 5 дистанционных разборов домашних заданий\n"
        "• 2,5 месяца в поддерживающем кругу таких же родителей\n"
        "• Дети + родители вместе — учимся, играем, растем\n\n"
        "📚 **ПРОГРАММА (6 модулей)**\n"
        "💚 Обида  |  ☀️ Радость  |  🌙 Страх\n"
        "🔥 Злость  |  💧 Грусть  |  ❤️ Любовь\n\n"
        "🎁 **ВСЕМ УЧАСТНИКАМ:**\n"
        "• Чат поддержки с куратором\n"
        "• Сертификат о прохождении курса\n\n"
        "📍 **СТАРТ: МАРТ 2026**\n"
        "Мест немного. Группы маленькие — чтобы каждому хватило внимания."
    )
    await message.answer(text, parse_mode="Markdown")

# ========== ТАРИФЫ ==========
@router.message(F.text == "📋 Тарифы")
async def show_tariffs(message: Message):
    await message.answer(
        "Выберите подходящий тариф:",
        reply_markup=get_tariffs_keyboard()
    )

@router.callback_query(F.data.startswith("tariff_"))
async def tariff_selected(callback: CallbackQuery, state: FSMContext):
    tariff_key = callback.data.split("_")[1]
    tariff = config.TARIFFS.get(tariff_key)
    if not tariff:
        await callback.answer("Тариф не найден")
        return

    await state.update_data(selected_tariff=tariff_key)

    # Общая информация для всех тарифов
    common_gifts = "🎁 **В подарок:**\n• Чат поддержки\n• Сертификат о прохождении"

    text = (
        f"💰 **Тариф: {tariff['name']}**\n\n"
        f"**Цена:** {tariff['price'] // 100} руб.\n\n"
        f"**В тариф входит:**\n{tariff['description']}\n\n"
        f"{common_gifts}\n\n"
        "Нажмите «Оплатить» для перехода к платежу."
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{tariff_key}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_tariffs")]
            ]
        ),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_tariffs")
async def back_to_tariffs(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите подходящий тариф:",
        reply_markup=get_tariffs_keyboard()
    )
    await callback.answer()

# ========== ПЛАТЕЖИ ==========
@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    tariff_key = callback.data.split("_")[1]
    tariff = config.TARIFFS.get(tariff_key)
    if not tariff:
        await callback.answer("Ошибка: тариф не найден")
        return

    prices = [LabeledPrice(label=tariff['name'], amount=tariff['price'])]
    payload = f"{callback.from_user.id}_{tariff_key}_{uuid.uuid4()}"

    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"Оплата тарифа «{tariff['name']}»",
        description=tariff['description'][:100],  # первые 100 символов
        payload=payload,
        provider_token=config.PAYMENTS_PROVIDER_TOKEN,
        currency=config.CURRENCY,
        prices=prices,
        start_parameter="course_payment"
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    payment = message.successful_payment
    payload = payment.invoice_payload
    user_id = message.from_user.id
    tariff_key = payload.split("_")[1]  # формат: user_id_tariffkey_uuid

    # Сохраняем платёж
    save_payment(
        user_id=user_id,
        amount=payment.total_amount,
        currency=payment.currency,
        tariff=tariff_key,
        payment_id=payload,
        status='confirmed'
    )

    # Активируем подписку
    activate_subscription(user_id, tariff_key)

    await message.answer(
        "✅ **Оплата прошла успешно!**\n\n"
        "Ваша подписка активирована. Теперь у вас есть доступ ко всем материалам курса и чату поддержки.\n"
        "Старт курса — в марте 2026. Следите за новостями в нашем канале.\n\n"
        "Если остались вопросы — нажмите кнопку «🆘 Поддержка».",
        parse_mode="Markdown"
    )

# ========== ПРОФИЛЬ ==========
@router.message(F.text == "📱 Мой профиль")
async def my_profile(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user and user['is_active'] and check_subscription(user_id):
        end_date = user['subscription_end'][:10]  # YYYY-MM-DD
        tariff_name = config.TARIFFS.get(user['tariff'], {}).get('name', user['tariff'])
        await message.answer(
            f"📱 **Ваш профиль**\n\n"
            f"Тариф: **{tariff_name}**\n"
            f"Подписка активна до: **{end_date}**\n\n"
            f"Спасибо, что вы с нами! ❤️",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "У вас нет активной подписки. Выберите тариф в меню «📋 Тарифы».",
            reply_markup=main_menu
        )

# ========== ПОДДЕРЖКА ==========
@router.message(F.text == "🆘 Поддержка")
async def support_handler(message: Message):
    support_username = config.SUPPORT_USERNAME
    text = (
        "🆘 **Служба поддержки**\n\n"
        f"По всем вопросам обращайтесь к Татьяне Загородней:\n"
        f"👉 @{support_username}\n\n"
        "Мы обязательно поможем!"
    )
    await message.answer(text, parse_mode="Markdown")

# ========== ОСТАЛЬНЫЕ СООБЩЕНИЯ (ОПЦИОНАЛЬНО) ==========
@router.message()
async def unknown_message(message: Message):
    await message.answer("Извините, я не понимаю эту команду. Воспользуйтесь меню.")

