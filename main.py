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


rasylka = None


@dp.message_handler(commands=['start'])    # перехватчик команды /start
async def start(message):
    kb2 = types.ReplyKeyboardRemove()
    await bot.send_message(message.chat.id, f'Приветственное сообщение\n'
                                            f'/post - устроить рассылку\n'
                                            f'/help - все возможности бота', reply_markup=kb2)
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        pass


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
    await bot.send_message(message.chat.id, f'Введите текст поста и отправьте мне..')
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception:
        pass
    await Form.text.set()


@dp.message_handler(state=Form.text)  # Принимаем состояние
async def new_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:  # Устанавливаем состояние ожидания
        data['text'] = message.message_id
        await model_buttons(bot, message).rasylka_buttons()
        await Form.message_id.set()


@dp.message_handler(state=Form.message_id)  # Принимаем состояние
async def new_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:  # Устанавливаем состояние ожидания
        await bot.send_message(message.chat.id, 'рассылаю сообщение..⏳')
        await clients_base(bot, message, data['text'], auto_model=None, base=message.text).rasylka_v_bazu()
        await state.finish()


if __name__ == '__main__':
    # scheduler.add_job(statistic().obnulenie, "cron", day_of_week='mon-sun', hour=0)
    # scheduler.add_job(statistic().obnulenie, "interval", hours=6)
    # scheduler.start()
    executor.start_polling(dp, skip_updates=True)