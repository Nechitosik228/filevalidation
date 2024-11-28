import os
from os import getenv
from dotenv import load_dotenv
import asyncio
from typing import List

import cloudmersive_virus_api_client
from fastapi import UploadFile, Request, BackgroundTasks


from . import app

load_dotenv()

configuration = cloudmersive_virus_api_client.Configuration()
configuration.api_key["Apikey"] = getenv("API_KEY")
api_instance = cloudmersive_virus_api_client.ScanApi(
    cloudmersive_virus_api_client.ApiClient(configuration)
)

MAX_FILE_SIZE = 5 * 1024 * 1024
TMP_FOLDER = "tmp"
FORMATS = ["image/png", "image/gif"]

os.makedirs(TMP_FOLDER, exist_ok=True)


async def save_image(image: bytes, file_path: str):
    await asyncio.sleep(3)
    with open(file_path, "wb") as buffer:
        buffer.write(image)


@app.post("/upload_image")
async def upload(
    request: Request, images: List[UploadFile], background_tasks: BackgroundTasks
):
    folder = f"{TMP_FOLDER}/{id(request)}"
    os.mkdir(folder)

    images_list = []

    for image in images:
        if image.content_type in FORMATS and image.size < MAX_FILE_SIZE:
            images_list.append(f"{image.filename} {image.size} bytes")
            background_tasks.add_task(
                save_image,
                file_path=f"{folder}/{image.filename}",
                image=image.file.read(),
            )

    return f"images:{images_list},id:{id(request)}"


@app.post("/antivirus_check")
async def check_virus(file: UploadFile):
    finished_folder_path = os.path.join(TMP_FOLDER)
    finished_file_path = f"{finished_folder_path}/{file.filename}"
    with open(f"{finished_file_path}", "ab") as buffer:
        buffer.write(file.file.read())

    api_response = api_instance.scan_file(finished_file_path)
    os.remove(finished_file_path)
    return api_response
