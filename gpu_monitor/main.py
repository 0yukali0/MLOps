import asyncio
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pynvml
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

latest_stats = {}

log_path = "/var/log/gpu_monitor.log"
if not os.path.isfile(log_path):
    open(log_path, "a").close()

logger = logging.getLogger("gpu_monitor")
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter(
    "[%(asctime)s] %(message)s — %(levelname)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

logger.addHandler(handler)

MiB = 1024**2


def get_gpu_stats():
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
    gpus_info = {}

    for i in range(gpu_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        usage = util.gpu
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        allocated_mem = mem_info.used // MiB
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        if util.gpu > 90.0 or temp > 80:
            logger.warning(f"GPU{i} ({gpu_name}) util={usage}% temp={temp}°C")
        gpus_info[f"gpu{i}"] = {
            "usage": util.gpu,
            "temperature": temp,
            "allocated_mem": f"{allocated_mem}MiB",
        }

    pynvml.nvmlShutdown()
    return {
        "timestamp": datetime.now().strftime("%Y/%m/%d:%H:%M:%S"),
        "gpus": gpus_info,
    }


async def update_gpu_stats():
    global latest_stats
    while True:
        latest_stats = get_gpu_stats()
        await asyncio.sleep(30)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_gpu_stats())


@app.get("/metrics")
async def read_latest_stats():
    if latest_stats:
        return JSONResponse(content=latest_stats)
    else:
        return JSONResponse(
            content={"message": "GPU stats not available yet"}, status_code=503
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
