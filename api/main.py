import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from moviepy.editor import VideoFileClip
import uvicorn
import aiofiles
from fastapi.middleware.cors import CORSMiddleware

# Токен бота
TOKEN = "7637754216:AAF5Ak9uDOk0Xjhtsy4Rc3W9dx1Meo7ZxMk"  # Замените на свой токен

# Создаем FastAPI приложение
app = FastAPI()

# Настройка CORS для доступа к нашему API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем доступ с любых источников
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Директория для временных файлов
TEMP_DIR = "/tmp/temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Отдает статический файл index.html"""
    with open("static/index.html", "r") as f:
        return f.read()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Приветственное сообщение с кнопкой для WebApp"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Загрузить видео", web_app=WebAppInfo(url="https://vercelecirclepressvgltubot.vercel.app/"))]
    ])
    await message.answer("Привет! Нажми кнопку ниже, чтобы загрузить видео.", reply_markup=keyboard)

# Функция для конвертации видео в видеокружок
async def convert_to_round_video(input_path: str, output_path: str):
    """Конвертирует видео в формат видеокружка без потери качества"""
    clip = VideoFileClip(input_path)
    if clip.duration > 60:
        clip = clip.subclip(0, 60)
    size = min(clip.size)
    clip = clip.crop(x_center=clip.w / 2, y_center=clip.h / 2, width=size, height=size)
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast")
    clip.close()

# API для загрузки видео
@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    """Принимает загруженное видео и сохраняет его"""
    input_path = os.path.join(TEMP_DIR, file.filename)
    async with aiofiles.open(input_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    return {"status": "uploaded", "filename": file.filename}

# Функция обработки видео и отправки в чат
async def process_video(chat_id: int, filename: str):
    """Конвертирует видео в кружок и отправляет пользователю"""
    input_path = os.path.join(TEMP_DIR, filename)
    output_path = os.path.join(TEMP_DIR, f"{filename}_round.mp4")
    await convert_to_round_video(input_path, output_path)
    await bot.send_video_note(chat_id, FSInputFile(output_path))
    os.remove(input_path)
    os.remove(output_path)

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
