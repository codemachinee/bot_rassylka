from aiogram import Bot, executor, Dispatcher, types
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ContentType, Message
from datetime import datetime, timedelta
import time
from passwords import *
from functions import *

admin_account = igor

token = lemonade
# token = codemashine_test

bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    text = State()
    message_id = State()
    channel = State()
    wallet = State()


rasylka = None


@dp.message_handler(commands=['start'])    # перехватчик команды /start
async def start(message):
    await bot.send_message(message.chat.id, f"Welcome to the bookmaker.XYZ freebet bot! We're excited to have you "
                                            f"here. To get started, please send us the necessary information so "
                                            f"that we can give you your free bet. We can't wait to see you start "
                                            f"winning!\n\nCan you tell me which channel you're coming from? Just "
                                            f"type in the name below, please. 😊",
                           reply_markup=await model_buttons(bot, message).otmena_button())
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        pass
    await Form.channel.set()


@dp.message_handler(commands=['help'])
async def help(message):
    kb2 = types.ReplyKeyboardRemove()
    await bot.send_message(message.chat.id, f'Основные команды поддерживаемые ботом:', reply_markup=kb2)
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        pass


@dp.message_handler(commands=['post'])
async def post(message):
    await bot.send_message(message.chat.id, f'Введите текст/фото/видео/файл для рассылки и отправьте мне..',
                           reply_markup=await model_buttons(bot, message).otmena_button())
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        pass
    await Form.text.set()


@dp.message_handler(state=Form.text, content_types=['text', 'document', 'photo', 'video'])  # Принимаем состояние
async def new_message(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        kb2 = types.ReplyKeyboardRemove()
        await state.finish()
        await bot.send_message(message.chat.id, f'Действие отменено', reply_markup=kb2)
        await bot.delete_message(message.chat.id, (message.message_id - 1))
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        async with state.proxy() as data:  # Устанавливаем состояние ожидания
            data['text'] = message.message_id
            await model_buttons(bot, message).rasylka_buttons()
            await Form.message_id.set()


@dp.message_handler(state=Form.message_id)  # Принимаем состояние
async def new_message(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        kb2 = types.ReplyKeyboardRemove()
        await state.finish()
        await bot.send_message(message.chat.id, f'Действие отменено', reply_markup=kb2)
        await bot.delete_message(message.chat.id, (message.message_id - 1))
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        async with state.proxy() as data:  # Устанавливаем состояние ожидания
            await bot.send_message(message.chat.id, 'рассылаю сообщение..⏳')
            await clients_base(bot, message, data['text'], base=message.text).rasylka_v_bazu()
            await state.finish()


@dp.message_handler(state=Form.channel)  # Принимаем состояние
async def new_message(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        kb2 = types.ReplyKeyboardRemove()
        await state.finish()
        await bot.send_message(message.chat.id, f'Действие отменено', reply_markup=kb2)
        await bot.delete_message(message.chat.id, (message.message_id - 1))
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        async with state.proxy() as data:
            kb2 = types.ReplyKeyboardRemove()# Устанавливаем состояние ожидания
            data['channel'] = message.text
            await bot.send_message(message.chat.id, f'Please give us the address of your Ethereum wallet.',
                                   reply_markup=kb2)
            await bot.delete_message(message.chat.id, (message.message_id - 1))
            await bot.delete_message(message.chat.id, message.message_id)
            await Form.wallet.set()


@dp.message_handler(state=Form.wallet)  # Принимаем состояние
async def new_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:  # Устанавливаем состояние ожидания
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.edit_message_text('Thank you! We will send you a freebet soon if you meet the '
                                    'necessary requirements.', message.chat.id, (message.message_id - 1))
        await clients_base(bot, message).chec_and_record(data['channel'], message.text)
        await state.finish()

if __name__ == '__main__':
    # scheduler.add_job(statistic().obnulenie, "cron", day_of_week='mon-sun', hour=0)
    # scheduler.add_job(statistic().obnulenie, "interval", hours=6)
    # scheduler.start()
    executor.start_polling(dp, skip_updates=True)