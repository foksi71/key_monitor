# from telethon import TelegramClient, events
# import asyncio

# # Ваші API_ID і API_HASH
# API_ID = 21033220
# API_HASH = 'a15f244bc9d48bc70fa7e192fe6e47ec'

# # Список ID каналів для моніторингу
# MONITORED_CHANNELS = [
#     -1001800023562,  # EdgEarnings🐩
#     -1001762006702,  # EdgEarnings premium
#     -1002071220835,  # C H A N E L 🦎
#     -1001962975152,  # Lupo 💌
#     -1002191813151,  # SHELL
#     -1002185637554,  # Spark
#     -1002070685270,  # Blood
#     -1002318593261,  # екз вм
#     -1001178398345,  # мій канал
# ]

# # Ключові слова для пошуку (всі маленькими літерами)
# KEYWORDS = [
#     "скоро завдання",
#     "завдання на кошти",
#     "потрібно",
#     "обов'язково нік",
#     "завдання через",
#     "оплата",
#     "коп",
#     "грн",
# ]

# # Список ID або username користувачів/каналів для пересилання повідомлень
# TARGET_CHATS = [
#     868558137,  # @andryy_99
#     123456789,  # @neksiix
# ]

# # Ініціалізація клієнта
# client = TelegramClient('monitoring_session', API_ID, API_HASH)

# # Основна асинхронна функція
# async def main():
#     # Авторизація
#     print("Вхід у Telegram...")
#     await client.start()

#     # Перевірка авторизації
#     me = await client.get_me()
#     print(f"Ви увійшли як {me.first_name} (@{me.username})")

#     # Обробник для моніторингу нових повідомлень
#     @client.on(events.NewMessage(chats=MONITORED_CHANNELS))
#     async def message_handler(event):
#         # Отримуємо текст повідомлення
#         message_text = event.message.message.lower()  # Приводимо текст до нижнього регістру

#         # Перевіряємо, чи містить повідомлення одне з ключових слів
#         if any(keyword in message_text for keyword in KEYWORDS):
#             # Пересилаємо повідомлення всім в списку TARGET_CHATS
#             for target_chat in TARGET_CHATS:
#                 forwarded_message = await event.forward_to(target_chat)
#                 print(f"Повідомлення переслано: {message_text} до {target_chat}")

#                 # Видаляємо переслане повідомлення через пів години
#                 await asyncio.sleep(300)
#                 try:
#                     await client.delete_messages(target_chat, forwarded_message.id)
#                     print(f"Повідомлення видалено: {forwarded_message.id} з {target_chat}")
#                 except Exception as e:
#                     print(f"Не вдалося видалити повідомлення з {target_chat}: {e}")

#     print("Запуск моніторингу...")
#     await client.run_until_disconnected()

# # Запуск клієнта
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main()) 





from telethon import TelegramClient, events
from flask import Flask

from datetime import datetime
from zoneinfo import ZoneInfo  # для Python 3.9+

import asyncio
import threading
import os
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API-ключі
API_ID = 21033220
API_HASH = 'a15f244bc9d48bc70fa7e192fe6e47ec'
SESSION_NAME = 'main_account_session'

# Список каналів для моніторингу
MONITORED_CHANNELS = [
    -1001800023562,  # EdgEarnings🐩
    -1001762006702,  # EdgEarnings premium
    # -1002071220835,  # C H A N E L 🦎
    # -1001962975152,  # Lupo 💌
    -1002191813151,  # SHELL
    -1002185637554,  # Spark
    # -1002070685270,  # Blood
    -1002540770220,  # Velisse
    -1002318593261,  # екз вм
    -1001178398345,  # мій канал
]

# Ключові слова
KEYWORDS = [
    "скоро завдання",
    "завдання на кошти",
    "проголосувати",
    "підписатися",
    "потрібно",
    "потрібна",
    "обов'язково нік",
    "завдання через",
    "завдання о", 
    "підписка",
    "лайк",
    "коментар",
    "оплата",
    "відгук",
    "коп",
    "грн",
]

# Отримувачі (username або ID)
TARGET_ACCOUNTS = [
    'andryy_99', 'dim_gtr', 'maxx_py', 'kentvr01', 'romixsi', 'k_valer1', 'karpatyu', 'karnazh01',
]  #'neksiix'

# Ініціалізація Telegram клієнта
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Flask HTTP-сервер
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

# Обробка нових повідомлень
@client.on(events.NewMessage(chats=MONITORED_CHANNELS))
async def handle_new_message(event):
    # Київський час
    current_hour = datetime.now(ZoneInfo("Europe/Kyiv")).hour
    if 4 <= current_hour < 11:
        logger.info("Нічний режим активний – повідомлення ігноруються")
        return

    message_text = event.message.message.lower()

    if any(keyword in message_text for keyword in KEYWORDS):
        logger.info(f"Знайдено повідомлення: {event.message.message}")
        for account_id in TARGET_ACCOUNTS:
            try:
                entity = await client.get_entity(account_id)  # Отримання сутності
                forwarded_message = await client.forward_messages(entity, event.message)
                logger.info(f"Повідомлення переслано до {account_id}")

                asyncio.create_task(delete_message_after_delay(entity.id, forwarded_message.id, 600))
            except Exception as e:
                logger.error(f"Помилка при пересиланні до {account_id}: {e}")


# Видалення повідомлення із затримкою
async def delete_message_after_delay(chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(chat_id, message_id)
        logger.info(f"Повідомлення {message_id} видалено")
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення {message_id}: {e}")

# Запуск Telegram-клієнта
async def main():
    await client.start()
    me = await client.get_me()
    logger.info(f"Авторизовано як {me.first_name} (@{me.username})")
    await client.run_until_disconnected()

# Запуск клієнта в окремому потоці
def run_telegram_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# Запуск Flask-сервера
if __name__ == "__main__":
    threading.Thread(target=run_telegram_client, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
