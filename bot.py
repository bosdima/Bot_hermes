#!/usr/bin/env python3
"""
Telegram Bot for Hermes Agent with PC connection check
Single file bot with file exchange support and PC monitoring
Author: Bot_Proxy from Hermes Agent
Date: 18.10.2026
"""

import os
import sys
import json
import logging
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

try:
    import telebot
except ImportError:
    print("Installing required packages...")
    os.system("pip install pyTelegramBotAPI python-dotenv requests")
    import telebot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
BOT_TOKEN = os.getenv('BOT_TOKEN', '8737491152:AAFL_BSsUG1Q2nDLPfSu0-KgTPX0cXyW1EQ')
USER_ID = int(os.getenv('USER_ID', '128382766'))
WORKING_DIR = os.getenv('WORKING_DIR', './telegram-working')
PC_CONNECTION_URL = os.getenv('PC_CONNECTION_URL', 'http://localhost:8080')  # URL для связи с Hermes Agent

# Создание рабочих директорий
Path(WORKING_DIR).mkdir(parents=True, exist_ok=True)

class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
        self.setup_handlers()
        self.pc_connected = False
        self.last_pc_check = None
        logger.info("Telegram Bot initialized")
    
    def setup_handlers(self):
        """Настройка обработчиков сообщений"""
        
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            if message.from_id == USER_ID:
                pc_status = "✅ Подключен" if self.pc_connected else "❌ Не подключен"
                self.bot.reply_to(message, 
                    f"👋 Привет, {message.from_user.first_name}!\n\n"
                    f"🚀 <b>HERMES AGENT TELEGRAM BOT</b>\n\n"
                    f"✅ Работает на сервере\n"
                    f"📡 Готов принимать сообщения\n"
                    f"🖥️ Hermes Agent: {pc_status}\n"
                    f"🔄 Мониторинг сети активен\n\n"
                    f"📝 Напишите любое сообщение для теста!\n\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
                logger.info(f"Start command from user {USER_ID}")
            else:
                self.bot.reply_to(message, "❌ Доступ запрещен")
        
        @self.bot.message_handler(commands=['test'])
        def handle_test(message):
            if message.from_id == USER_ID:
                pc_status = "✅ Подключен" if self.pc_connected else "❌ Не подключен"
                test_text = (
                    f"🧪 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\n"
                    f"✅ Бот работает на сервере!\n"
                    f"🖥️ Hermes Agent: {pc_status}\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                )
                
                if self.pc_connected:
                    # Проверяем связь с Hermes Agent
                    try:
                        response = requests.get(f"{PC_CONNECTION_URL}/health", timeout=5)
                        if response.status_code == 200:
                            test_text += f"\n\n🎉 Hermes Agent отвечает!"
                        else:
                            test_text += f"\n\n⚠️ Hermes Agent не отвечает (код {response.status_code})"
                    except Exception as e:
                        test_text += f"\n\n❌ Hermes Agent недоступен: {str(e)}"
                
                self.bot.reply_to(message, test_text)
                logger.info("Test command executed")
            else:
                self.bot.reply_to(message, "❌ Доступ запрещен")
        
        @self.bot.message_handler(commands=['status'])
        def handle_status(message):
            if message.from_id == USER_ID:
                pc_status = "✅ Подключен" if self.pc_connected else "❌ Не подключен"
                last_check = self.last_pc_check.strftime('%d.%m.%Y %H:%M:%S') if self.last_pc_check else "Не проверялся"
                
                status_text = (
                    f"📊 <b>СТАТУС СИСТЕМЫ</b>\n\n"
                    f"✅ Бот: Запущен на сервере\n"
                    f"🖥️ Hermes Agent: {pc_status}\n"
                    f"🕐 Последняя проверка: {last_check}\n"
                    f"📁 Рабочая директория: {WORKING_DIR}\n"
                    f"🌐 URL связи: {PC_CONNECTION_URL}\n\n"
                    f"🎯 Напишите сообщение для теста!"
                )
                self.bot.reply_to(message, status_text)
                logger.info("Status command executed")
            else:
                self.bot.reply_to(message, "❌ Доступ запрещен")
        
        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            if message.from_id == USER_ID:
                help_text = (
                    f"ℹ️ <b>СПРАВОЧНИК КОМАНД</b>\n\n"
                    f"/start - Приветственное сообщение\n"
                    f"/test - Тестовое сообщение + проверка Hermes\n"
                    f"/status - Статус системы\n"
                    f"/help - Эта справка\n\n"
                    f"🔧 Бот передает все сообщения в Hermes Agent через файловую систему."
                )
                self.bot.reply_to(message, help_text)
                logger.info("Help command executed")
            else:
                self.bot.reply_to(message, "❌ Доступ запрещен")
        
        @self.bot.message_handler(commands=['check'])
        def handle_check(message):
            if message.from_id == USER_ID:
                self.check_pc_connection()
                pc_status = "✅ Подключен" if self.pc_connected else "❌ Не подключен"
                check_text = (
                    f"🔍 <b>ПРОВЕРКА СВЯЗИ С HERMES AGENT</b>\n\n"
                    f"🖥️ Статус: {pc_status}\n"
                    f"🕐 Время проверки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                    f"🌐 URL: {PC_CONNECTION_URL}\n\n"
                )
                
                if self.pc_connected:
                    check_text += "✅ Hermes Agent доступен!\n\n🎯 Бот готов передавать сообщения!"
                else:
                    check_text += "❌ Hermes Agent недоступен!\n\n🔧 Проверьте:\n1. Hermes Agent запущен\n2. Сеть между сервером и ПК\n3. Firewall настройки"
                
                self.bot.reply_to(message, check_text)
                logger.info("Check command executed")
            else:
                self.bot.reply_to(message, "❌ Доступ запрещен")
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message):
            """Обработка текстовых сообщений"""
            if message.from_id != USER_ID:
                self.bot.reply_to(message, "❌ Доступ запрещен")
                return
            
            logger.info(f"Received message from user {USER_ID}: {message.text}")
            
            try:
                # Проверяем связь с Hermes Agent
                if not self.pc_connected:
                    self.check_pc_connection()
                
                # Формируем ответ
                pc_status = "✅ Hermes Agent готов" if self.pc_connected else "⚠️ Hermes Agent недоступен"
                
                # Отправляем подтверждение
                confirmation_text = (
                    f"✅ <b>ПОДТВЕРЖДЕНИЕ</b> ✅\n\n"
                    f"📨 Ваше сообщение получено серверным ботом!\n\n"
                    f"Текст: <i>{message.text}</i>\n"
                    f"🖥️ Hermes Agent: {pc_status}\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                )
                
                if self.pc_connected:
                    confirmation_text += f"🎯 Сообщение будет передано в Hermes Agent для обработки!"
                else:
                    confirmation_text += f"⚠️ Hermes Agent недоступен, сообщение сохранено в файл!"
                
                self.bot.reply_to(message, confirmation_text)
                logger.info("Confirmation sent to user")
                
                # Сохраняем сообщение в файл
                message_data = {
                    "id": int(time.time()),
                    "type": "telegram_incoming_message",
                    "action": "process_and_reply",
                    "data": {
                        "chat_id": USER_ID,
                        "reply_to_message_id": message.message_id,
                        "from_username": message.from_user.username or "unknown",
                        "from_name": message.from_user.first_name or "Unknown User",
                        "received_text": message.text,
                        "received_at": datetime.now().isoformat(),
                        "server_bot_status": "active",
                        "pc_connected": self.pc_connected,
                        "pc_connection_url": PC_CONNECTION_URL
                    },
                    "status": "received",
                    "processed": False
                }
                
                # Сохраняем в рабочий каталог
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(WORKING_DIR, f"server_message_{timestamp}.json")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(message_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Message saved to: {output_file}")
                
                # Если Hermes Agent доступен, отправляем уведомление
                if self.pc_connected:
                    try:
                        # Пытаемся отправить уведомление Hermes Agent
                        response = requests.post(
                            f"{PC_CONNECTION_URL}/telegram_message",
                            json=message_data,
                            timeout=10
                        )
                        if response.status_code == 200:
                            logger.info("Message successfully sent to Hermes Agent")
                        else:
                            logger.warning(f"Hermes Agent responded with status {response.status_code}")
                    except Exception as e:
                        logger.error(f"Failed to send message to Hermes Agent: {e}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
                # Сохраняем ошибку в файл
                error_data = {
                    "id": int(time.time()),
                    "type": "telegram_incoming_message",
                    "action": "process_and_reply",
                    "data": {
                        "chat_id": USER_ID,
                        "reply_to_message_id": message.message_id,
                        "from_username": message.from_user.username or "unknown",
                        "from_name": message.from_user.first_name or "Unknown User",
                        "received_text": message.text,
                        "received_at": datetime.now().isoformat(),
                        "server_bot_status": "error",
                        "error_message": str(e)
                    },
                    "status": "error",
                    "processed": False
                }
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                error_file = os.path.join(WORKING_DIR, f"server_message_error_{timestamp}.json")
                
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(error_data, f, ensure_ascii=False, indent=2)
                
                logger.error(f"Error saved to: {error_file}")
                
                # Отправляем сообщение об ошибке
                error_response = (
                    f"⚠️ <b>ОШИБКА ОБРАБОТКИ</b> ⚠️\n\n"
                    f"Ваше сообщение получено, но возникла ошибка:\n"
                    f"<code>{str(e)}</code>\n\n"
                    f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                    f"🔧 Бот работает, но требует внимания"
                )
                self.bot.reply_to(message, error_response)
    
    def check_pc_connection(self):
        """Проверка связи с Hermes Agent на ПК"""
        try:
            # Проверяем доступность Hermes Agent
            response = requests.get(f"{PC_CONNECTION_URL}/health", timeout=5)
            if response.status_code == 200:
                self.pc_connected = True
                self.last_pc_check = datetime.now()
                logger.info("Hermes Agent connection successful")
            else:
                self.pc_connected = False
                self.last_pc_check = datetime.now()
                logger.warning(f"Hermes Agent connection failed with status {response.status_code}")
        except Exception as e:
            self.pc_connected = False
            self.last_pc_check = datetime.now()
            logger.error(f"Hermes Agent connection error: {e}")
    
    def send_welcome_message(self):
        """Отправка приветственного сообщения пользователю"""
        try:
            # Проверяем связь с Hermes Agent
            self.check_pc_connection()
            pc_status = "✅ Подключен" if self.pc_connected else "❌ Не подключен"
            
            welcome_text = (
                f"🚀 <b>BOTPROXY СЕРВЕР ЗАПУЩЕН!</b> 🚀\n\n"
                f"✅ Работает на сервере\n"
                f"📡 Готов принимать ваши сообщения\n"
                f"🖥️ Hermes Agent: {pc_status}\n\n"
                f"👤 Пользователь: @bosdima\n"
                f"🤖 Бот: @AiDSeek_bot\n"
                f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                f"🎯 Отправьте любое сообщение для теста!\n"
                f"📱 Используйте /check для проверки связи с Hermes"
            )
            self.bot.send_message(USER_ID, welcome_text)
            logger.info("Welcome message sent to user")
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
    
    def run(self):
        """Запуск бота"""
        try:
            logger.info("Starting Telegram Bot...")
            logger.info(f"Bot Token: {BOT_TOKEN[:10]}...")
            logger.info(f"User ID: {USER_ID}")
            logger.info(f"Working Directory: {WORKING_DIR}")
            logger.info(f"PC Connection URL: {PC_CONNECTION_URL}")
            
            # Проверяем связь с Hermes Agent при запуске
            self.check_pc_connection()
            
            # Отправка приветственного сообщения
            self.send_welcome_message()
            
            # Запуск бота
            logger.info("Bot is running... Press Ctrl+C to stop")
            self.bot.polling(none_stop=True)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()