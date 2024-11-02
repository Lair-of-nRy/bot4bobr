import aiohttp
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

TELEGRAM_TOKEN = ''
WEATHER_API_KEY = ''
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def get_weather(city_name):
    logging.info(f"Получение погоды для: {city_name}")
    params = {
        'q': city_name,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WEATHER_URL, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                humidity = data['main']['humidity']
                return f"Погода в {city_name}:\nТемпература: {temperature}°C\nВлажность: {humidity}%\nОписание: {weather_description}"
    except asyncio.TimeoutError:
        logging.error("Время ожидания запроса истекло")
        return "Сервер погоды не отвечает"
    except aiohttp.ClientError as err:
        logging.error(f"Ошибка запроса: {err}")
        return "Произошла ошибка при получении данных"

@dp.message(Command(commands=['start']))
async def start_command(message: Message):
    logging.info("Обработка команды /start")
    await message.reply("Введите название города")

@dp.message()
async def send_weather(message: Message):
    city_name = message.text
    logging.info(f"Обработка сообщения с названием: {city_name}")
    weather_info = await get_weather(city_name)
    await message.reply(weather_info)

async def main():
    logging.info("Поехали")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу")
    ])
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
