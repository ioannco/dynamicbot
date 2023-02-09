"""
    Telegram event handlers
"""
from telegram.ext import (
    Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)

from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON

from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.main import bot

from django.dispatch import receiver
from django.db.models.signals import post_save


from users.models import User
from telegram import *
from users.models import Reply

def start_menu_buttons():
    buttons = []

    for rep in Reply.objects.all():
        buttons.append(
            InlineKeyboardButton(rep.button_label, callback_data=f'REP_{rep.id}')
        )

    matrix = []

    start = 0
    end = len(buttons)
    step = 2
    for i in range(start, end, step):
        x = i
        matrix.append(buttons[x:x + step])

    markup = InlineKeyboardMarkup(matrix)
    return markup

def start_page_handler(update, context):
    update.message.reply_text(text='Здравствуйте!', reply_markup=start_menu_buttons())


def start_menu_handler(update, context):
    context.bot.edit_message_text(
        text='Главное меню',
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=start_menu_buttons()
    )


def reply_handler(update, context):
    id = int(update.callback_query.data[len('REP_'):])
    rep = Reply.objects.get(id=id)

    buttons = [[
        InlineKeyboardButton('Меню', callback_data='STARTMENU')
    ]]

    context.bot.edit_message_text(
        text=rep.button_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", start_page_handler))

    regex = '^('

    for rep in Reply.objects.all():
        regex += f'REP_{rep.id}|'

    regex = regex[:-1]

    regex += ')'

    dp.add_handler(CallbackQueryHandler(reply_handler, pattern=regex))
    dp.add_handler(CallbackQueryHandler(start_menu_handler, pattern='STARTMENU'))


    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
