import os
from environs import Env

env = Env()
env.read_env()

class Config:
    BOT_TOKEN = env.str('BOT_TOKEN')
    PAYMENTS_PROVIDER_TOKEN = env.str('PAYMENTS_PROVIDER_TOKEN')
    ADMIN_ID = env.int('ADMIN_ID')
    SUPPORT_USERNAME = env.str('SUPPORT_USERNAME', 'TatyanaZagorodnyaya')  # username Татьяны

    # Длительность подписки в днях (2,5 месяца ≈ 75 дней)
    SUBSCRIPTION_DAYS = 75

    # Цены в копейках!
    TARIFFS = {
        'minimum': {
            'name': 'МИНИМУМ',
            'price': 600000,          # 6000 руб
            'description': (
                '· 6 очных занятий\n'
                '· Все пособия (6 PDF-гайдов)'
            )
        },
        'optimal': {
            'name': 'ОПТИМУМ',
            'price': 900000,          # 9000 руб
            'description': (
                '· 6 очных занятий\n'
                '· 5 дистанционных разборов домашних заданий\n'
                '· Все пособия (6 PDF-гайдов)'
            )
        },
        'premium': {
            'name': 'ПРЕМИУМ',
            'price': 1200000,         # 12000 руб
            'description': (
                '· 6 очных занятий\n'
                '· 5 дистанционных разборов ДЗ\n'
                '· 3 индивидуальные консультации: психолог + профориентация + нутрициолог\n'
                '· Все пособия (6 PDF-гайдов)\n'
                '· Личный куратор на весь курс'
            )
        }
    }

    CURRENCY = 'RUB'

config = Config()