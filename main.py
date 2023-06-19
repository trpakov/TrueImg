import json
from typing import Optional, Union
from fastapi import HTTPException
import os
import time
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, Response, Request
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
# import warnings; warnings.filterwarnings("ignore")
from glob import glob
import collections
import uuid
from pathlib import Path
import hashlib

import aiofiles
import cv2
import numpy as np
import scipy.sparse
from fastapi import FastAPI, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse
from scipy.fft import dctn, idctn
from skimage.color import rgb2ycbcr, ycbcr2rgb
from backend.const import REDIS_URL, ID_WMi_tuple
import backend.watermark as watermark
from pydantic import HttpUrl
import requests
import redis.asyncio as redis


app = FastAPI()

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")


@app.on_event("startup")
async def init():
    global rd
    rd = await redis.from_url(REDIS_URL, decode_responses=True)


@app.on_event("shutdown")
async def shutdown():
    await rd.close()

@app.get("/")
async def root():
    return FileResponse('frontend/index.html')


@app.get("/embed")
async def embed():
    return FileResponse('frontend/embed.html')


@app.get("/detect")
async def detect():
    return FileResponse('frontend/detect.html')


@app.get("/about")
async def about():
    return FileResponse('frontend/about.html')


@app.post(
    "/embed_watermark",
    status_code=201,
    summary="Add an invisible watermark to an image.",
    tags=["watermark"],
)
async def embed_watermark_file(
    file: UploadFile,
    Wi: Union[str, int] = 123462,
    Li: int = Query(10000, gt=1000),
    ni: int = Query(100, gt=0),
    mi: int = Query(100, gt=0),
    cache: bool = True,
):
    """
    Add an invisible watermark to provided image (multipart/form upload).
    Supported parameters:

    - **file**: image to be used for processing
    - **Wi**: watermark code (used as a seed for the PRNG)
    - **Li**: watermark length
    - **ni**: embedding matrix starting row (1-based)
    - **mi**: embedding matrix starting column (1-based)
    """

    # Form paths for input and watermarked image
    id = uuid.uuid4().hex
    input_path = Path("backend", "input", "embed", f"{file.filename}")
    output_path = Path("backend", "results", id).with_suffix(".jpg")

    # Try to save the file
    try:
        async with aiofiles.open(input_path, "wb") as f:
            content = await file.read()
            await f.write(content)
    except Exception:
        raise HTTPException(400, "Unsupported file")

    # Init watermark tuple
    ID_WMi = ID_WMi_tuple(Wi=Wi, Li=Li, ni=ni, mi=mi)

    sha256 = hashlib.sha256(content)
    sha256.update(repr(ID_WMi).encode('utf-8'))
    sha256.update('/embed'.encode('utf-8'))
    sha256 = sha256.hexdigest()

    if cache and (cached := await rd.get(sha256)) and Path('backend', 'results', f'{cached}.jpg').is_file():
        return PlainTextResponse(cached)

    # Embed watermark
    watermark.embed_watermark(input_path, output_path, ID_WMi)

    await rd.set(sha256, id)

    return PlainTextResponse(id)


@app.get(
    "/embed_watermark",
    status_code=201,
    summary="Add an invisible watermark to an image.",
    tags=["watermark"],
)
async def embed_watermark_url(
    url: HttpUrl,
    Wi: Union[str, int] = 123462,
    Li: int = Query(10000, gt=1000),
    ni: int = Query(100, gt=0),
    mi: int = Query(100, gt=0),
    cache: bool = True,
):
    """
    Add an invisible watermark to provided image (via URL).
    Supported parameters:

    - **url**: url of the image to be used for processing
    - **Wi**: watermark code (used as a seed for the PRNG)
    - **Li**: watermark length
    - **ni**: embedding matrix starting row (1-based)
    - **mi**: embedding matrix starting column (1-based)
    """

    # Form paths for input and watermarked image
    id = uuid.uuid4().hex
    input_path = Path("backend", "input", "embed", f"{Path(str(url)).name}")
    output_path = Path("backend", "results", id).with_suffix(".jpg")

    # Try to save the file
    try:
        async with aiofiles.open(input_path, "wb") as f:
            content = requests.get(url, allow_redirects=True).content
            await f.write(content)
    except Exception:
        raise HTTPException(400, "Unsupported file")

    # Init watermark tuple
    ID_WMi = ID_WMi_tuple(Wi=Wi, Li=Li, ni=ni, mi=mi)

    sha256 = hashlib.sha256(content)
    sha256.update(repr(ID_WMi).encode('utf-8'))
    sha256.update('/embed'.encode('utf-8'))
    sha256 = sha256.hexdigest()

    if cache and (cached := await rd.get(sha256)) and Path('backend', 'results', f'{cached}.jpg').is_file():
        return PlainTextResponse(cached)

    # Embed watermark
    watermark.embed_watermark(input_path, output_path, ID_WMi)

    await rd.set(sha256, id)

    return PlainTextResponse(id)


@app.post(
    "/read_watermark",
    summary="Check an image for an invisible watermark.",
    tags=["watermark"],
)
async def read_watermark_file(
    file: UploadFile,
    Wi: Union[str, int] = 123462,
    Li: int = Query(10000, gt=1000),
    ni: int = Query(100, gt=0),
    mi: int = Query(100, gt=0),
    cache: bool = True,
):
    """
    Check if the provided image (multipart/form upload) contains an invisible watermark.
    Supported parameters:

    - **file**: image to be used for processing
    - **Wi**: watermark code (used as a seed for the PRNG)
    - **Li**: watermark length
    - **ni**: embedding matrix starting row (1-based)
    - **mi**: embedding matrix starting column (1-based)
    """

    # Form path for input image
    input_path = Path("backend", "input", "detect", f"{file.filename}")
    
    # Try to save the file
    try:
        async with aiofiles.open(input_path, "wb") as f:
            content = await file.read()
            await f.write(content)
    except Exception:
        raise HTTPException(400, "Unsupported file")

    # Init watermark tuple
    ID_WMi = ID_WMi_tuple(Wi=Wi, Li=Li, ni=ni, mi=mi)

    sha256 = hashlib.sha256(content)
    sha256.update(repr(ID_WMi).encode('utf-8'))
    sha256.update('/read'.encode('utf-8'))
    sha256 = sha256.hexdigest()

    if cache and (cached := await rd.get(sha256)):
        return JSONResponse(json.loads(cached))

    # Detect watermark
    detection = watermark.read_watermark(input_path, ID_WMi)

    await rd.set(sha256, json.dumps(detection))

    return JSONResponse(detection)


@app.get(
    "/read_watermark",
    summary="Check an image for an invisible watermark.",
    tags=["watermark"],
)
async def read_watermark_url(
    url: HttpUrl,
    Wi: Union[str, int] = 123462,
    Li: int = Query(10000, gt=1000),
    ni: int = Query(100, gt=0),
    mi: int = Query(100, gt=0),
    cache: bool = True,
):
    """
    Check if the provided image (multipart/form upload) contains an invisible watermark.
    Supported parameters:

    - **file**: image to be used for processing
    - **Wi**: watermark code (used as a seed for the PRNG)
    - **Li**: watermark length
    - **ni**: embedding matrix starting row (1-based)
    - **mi**: embedding matrix starting column (1-based)
    """

    # Form path for input image
    input_path = Path("backend", "input", "detect", f"{Path(str(url)).name}")
    
    # Try to save the file
    try:
        async with aiofiles.open(input_path, "wb") as f:
            content = requests.get(url, allow_redirects=True).content
            await f.write(content)
    except Exception:
        raise HTTPException(400, "Unsupported file")

    # Init watermark tuple
    ID_WMi = ID_WMi_tuple(Wi=Wi, Li=Li, ni=ni, mi=mi)

    sha256 = hashlib.sha256(content)
    sha256.update(repr(ID_WMi).encode('utf-8'))
    sha256.update('/read'.encode('utf-8'))
    sha256 = sha256.hexdigest()

    if cache and (cached := await rd.get(sha256)):
        return JSONResponse(json.loads(cached))

    # Detect watermark
    detection = watermark.read_watermark(input_path, ID_WMi)

    await rd.set(sha256, json.dumps(detection))

    return JSONResponse(detection)


@app.get("/{id}")
async def get_img(id: str):
    
    path = glob(f'backend/results/{id}.*')

    if len(path) == 1:
        return FileResponse(path[0])
    else:
        raise HTTPException(status_code=404, detail="Image not found")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start_time)
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=False)

