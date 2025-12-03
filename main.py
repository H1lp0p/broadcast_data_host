import asyncio
import socket
from fastapi import FastAPI, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Form
import uvicorn

from pathlib import Path

app = FastAPI()

# Разрешаем CORS для всех источников (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация
BROADCAST_PORT = 8888  # Порт для broadcast сообщений
SERVER_PORT = 8000     # Порт для HTTP сервера
SECRET_KEY = "b3405fbdf36b61f06f3a91054c62d68cd963e45b658f0834e44d0b76e7659c4d"  # Секретный ключ для идентификации

UPLOADS_DIR = "./uploads"   # Директория для сохранения загруженных файлов

if not Path(UPLOADS_DIR).exists():
    Path(UPLOADS_DIR).mkdir()

class UDPServer:
    def __init__(self):
        self.socket = None
    
    async def start(self):
        """Запуск UDP сервера для обработки broadcast запросов"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(('', BROADCAST_PORT))
        
        print(f"UDP сервер запущен на порту {BROADCAST_PORT}")
        
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                await self.handle_broadcast(data, addr)
            except Exception as e:
                print(f"Ошибка при обработке UDP пакета: {e}")
    
    async def handle_broadcast(self, data: bytes, addr: tuple):
        """Обработка broadcast запроса"""
        try:
            message = data.decode('utf-8').strip()
            print(f"Получен broadcast запрос от {addr}: {message}")
            
            # Проверяем, является ли сообщение нашим секретным запросом
            if message == f"DISCOVER_{SECRET_KEY}":
                response = f"FOUND_{SERVER_PORT}"
                self.socket.sendto(response.encode('utf-8'), addr)
                print(f"Отправлен ответ клиенту {addr}: {response}")
        except Exception as e:
            print(f"Ошибка при обработке запроса: {e}")

# HTTP эндпоинты для загрузки файлов
@app.post("/upload")
async def upload_file(
    response: Response,
    file: UploadFile = File(...),
    timestamp: str = Form(...),
    dir_name: str = Form(...)
):
    print(f"Получен файл: {file.filename} с меткой времени: {timestamp}")
    # Сохраняем файл

    path = Path(f"{UPLOADS_DIR}/{dir_name}")
    if not path.exists() or not path.is_dir():
        path.mkdir()

    file_location = f"{UPLOADS_DIR}/{dir_name}/{file.filename}"
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {
        "status": "success",
        "filename": file.filename,
        "size": len(content),
        "timestamp": timestamp,
        "dir_name": dir_name
    }

@app.get("/")
async def root():
    return {"message": "File server is running"}

@app.get("/check")
async def check():
    print("Проверка соединения пройдена!")
    return {"msg": "good"}

@app.get("/upload/mkdir/{dir_name}")
async def mkdir(dir_name: str, response: Response):

    if len(dir_name.replace(" ", "")) == 0:
        response.status_code = "500"
        return f"incorrect dir_name: {dir_name}"
        

    path = Path(f"{UPLOADS_DIR}/{dir_name}")
    if path.exists() and path.is_dir():
        return "Ok"
    
    try:
        path.mkdir()
        return dir_name
    except:
        print(f"Error on mkDir {dir_name}")


# Запуск сервера
if __name__ == "__main__":
    # Запускаем UDP сервер в отдельном потоке
    import threading
    udp_server = UDPServer()
    
    def run_udp_server():
        asyncio.run(udp_server.start())
    
    udp_thread = threading.Thread(target=run_udp_server, daemon=True)
    udp_thread.start()
    
    # Запускаем HTTP сервер
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)