from aiogram import types
import gspread
# библиотека проверки даты
from datetime import *
# библиотека рандома
from random import *
from passwords import *
import pytz
tz_moscow = pytz.timezone('Europe/Moscow')

admin_account = igor


class model_buttons: # класс формирования клавиатур

    def __init__(self, bot, message, **kwargs):
        self.bot = bot
        self.message = message
        self.kwargs = kwargs

    async def rasylka_buttons(self):
        kb5 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        but1 = types.KeyboardButton(text='база общая')
        but2 = types.KeyboardButton(text='база рассылки')
        kb5.add(but1, but2)
        await self.bot.send_message(self.message.chat.id, f'Выберите базу для рассылки', reply_markup=kb5)

    async def otmena_button(self):
        kb3 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        but1 = types.KeyboardButton(text='Отмена')
        kb3.add(but1)
        return kb3



class clients_base:  # класс базы данных

    def __init__(self, bot, message, message_id=None, base=None):
        self.bot = bot
        self.message = message
        self.message_id = message_id
        self.base = base
        gc = gspread.service_account(filename='base_key.json')  # доступ к гугл табл по ключевому файлу аккаунта разраба
        # открытие таблицы по юрл адресу:
        sh = gc.open('base')
        self.worksheet = sh.worksheet('база общая')  # выбор листа 'общая база клиентов' таблицы
        self.worksheet2 = sh.worksheet('база рассылки')

    async def chec_and_record(self, channel, wallet):  # функция поиска и записи в базу
        global tz_moscow
        worksheet_len = len(self.worksheet.col_values(1)) + 1  # поиск первой свободной ячейки для записи во 2 столбце
        worksheet_len2 = len(self.worksheet2.col_values(1)) + 1
        # await self.bot.send_message(admin_account, 'Пробиваю базу..')
        # await self.bot.send_message(admin_account, '...')
        # if str(self.message.chat.id) in self.worksheet.col_values(1):
        #     await self.bot.send_message(admin_account, ' Клиент есть в базе')
        # else:
        #     await self.bot.send_message(admin_account, f'Клиент добавлен в базу\n'
        #             f'База: '
        #             f'https://docs.google.com/spreadsheets/d/1M3PHqj06Ex1_oXKuyR8CZCjl4j67qxvQUNNfcA3WjyY/edit#gid=0')
        self.worksheet.update(f'A{worksheet_len}:F{worksheet_len}', [[self.message.chat.id, self.message.from_user.username,
                              channel, wallet, self.message.from_user.first_name, str(datetime.now(tz_moscow).date())]])
        self.worksheet2.update(f'A{worksheet_len2}:F{worksheet_len2}', [[self.message.chat.id,
                                                                       self.message.from_user.username, channel,
                                                                       wallet, self.message.from_user.first_name,
                                                                       str(datetime.now(tz_moscow).date())]])
        await self.bot.send_message(admin_account, f'Клиент @{self.message.from_user.username} добавлен в базу\n'
                                                   f'База: '
                                                   f'https://docs.google.com/spreadsheets/d/1CrhViB9dhtaAxcyu_n3S1l0UmpyRecTH9PCV5Lon0_U/edit?usp=sharing')

    async def perevod_v_bazu(self):  # функция перевода из базы потенциальных клиентов в базу старых клиентов
        try:
            worksheet_len3 = len(self.worksheet3.col_values(1)) + 1
            cell = self.worksheet.find(self.perehvat)  # поиск ячейки с данными по ключевому слову
            # запись клиента в свободную строку базы старых клиентов:
            self.worksheet3.update(f'A{worksheet_len3}:F{worksheet_len3}', [self.worksheet.row_values(cell.row)])
            self.worksheet2.batch_clear([f"A{cell.row}:F{cell.row}"])  # удаление клиента из базы потенциальных
            await self.bot.send_message(admin_account, 'Птичка в клетке ✅')
        except AttributeError:
            await self.bot.send_message(admin_account, 'Ошибка, пользователь отсутствует, будь внимательнее если осознал свой '
                                                'косяк воспользуйся командой /next_level_base снова')

    async def rasylka_v_bazu(self):  # функция рассылки постов в базы
        kb5 = types.ReplyKeyboardRemove()  # удаление клавиатуры
        kb6 = types.InlineKeyboardMarkup(row_width=1)
        but1 = types.InlineKeyboardButton(text='Конечно!', callback_data='btn')
        kb6.add(but1)
        if self.base == 'база общая':
            for i in range(1, len(self.worksheet.col_values(1))):
                try:
                    await self.bot.copy_message(self.worksheet.col_values(1)[i], self.message.chat.id,
                                                self.message_id, reply_markup=kb5)
                except Exception:
                    await self.bot.send_message(admin_account, f'Босс, похоже @{self.worksheet.col_values(2)[i]} меня '
                                                               f'заблокировал. Рассылка невозможна.', reply_markup=kb5)
            await self.bot.edit_message_text(f'Босс, рассылка в общую базу выполнена ✅', self.message.chat.id,
                                             message_id=self.message.message_id + 1)
        if self.base == 'база рассылки':
            for i in range(1, len(self.worksheet2.col_values(1))):
                try:
                    await self.bot.copy_message(self.worksheet2.col_values(1)[i], self.message.chat.id,
                                                self.message_id, reply_markup=kb5)
                except Exception:
                    await self.bot.send_message(self.message.chat.id, f'Босс, похоже @{self.worksheet2.col_values(2)[i]} '
                                                                      f'заблочил меня. Рассылка невозможна',
                                                reply_markup=kb5)
            await self.bot.edit_message_text(f'Босс, рассылка в базу рассылки выполнена ✅', self.message.chat.id,
                                             message_id=self.message.message_id + 1)

