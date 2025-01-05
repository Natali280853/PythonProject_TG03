import sqlite3
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Эта библиотека нужна для сохранения контекста между сообщениями, чтобы сохранять информацию
# между запросами и использовать ее, например, в базе данных.
from aiogram.fsm.context import FSMContext

# импортируем библиотеку для работы с состояниями, или другими словами, для работы
# с информацией, передаваемой пользователем. Здесь будет использоваться класс State для работы
# с отдельными состояниями пользователей и StatesGroup для группировки состояний.
from aiogram.fsm.state import State, StatesGroup

# импортируем библиотеку для сохранения состояния в оперативной памяти:
from aiogram.fsm.storage.memory import MemoryStorage

# библиотека — IOHTTP для выполнения асинхронных HTTP-запросов. Наш бот будет подключаться
# к API прогнозов погоды и выдавать прогноз для конкретного пользователя, город которого будет
# записан в базе данных.
# import aiohttp

# здесь можно также использовать логирование, что, по сути, является ведением журнала событий.
# Это полезно для записи сообщений, событий или информации о работе программы.
# Для этого импортируем библиотеку Logging:
import logging

from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Создание базы данных и таблицы
def create_database():
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            grade TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


create_database()


# Определение состояний
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)


@dp.message(Form.name)  # =бот получил имя
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)  # =бот получил возраст
async def age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=message.text)
        await message.answer("В каком классе ты учишься?")
        await state.set_state(Form.grade)
    except ValueError:
        await message.reply("Пожалуйста, введите корректный возраст.")


@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    # await state.update_data(grade=message.text)
    data = await state.get_data()
    name = data.get('name')
    age = data.get('age')
    grade = message.text

    # Сохранение данных в базу данных
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO students (name, age, grade) VALUES (?, ?, ?)', (name, age, grade))
    conn.commit()
    conn.close()

    await message.reply(f"Спасибо, {name}! Ваши данные сохранены.\nВозраст: {age}\nКласс: {grade}")
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
