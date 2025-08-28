import time
import requests
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from PIL import Image
import matplotlib.pyplot as plt

# ------------------------------
# Función de descarga
# ------------------------------
def download_image(url, filename):
    resp = requests.get(url, timeout=10)
    with open(filename, "wb") as f:
        f.write(resp.content)
    return filename

IMAGES = [
    "https://atlnacional.com.co/wp-content/webp-express/webp-images/uploads/2022/02/Mascota.jpg.webp",
    "https://atlnacional.com.co/wp-content/webp-express/webp-images/uploads/2022/02/Escudo-1.jpg.webp"
]


# ------------------------------
# Threading
# ------------------------------
def download_with_threads():
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(
            download_image,
            IMAGES,
            [f"th_{i}.jpg" for i in range(len(IMAGES))]
        ))
    return results

# ------------------------------
# Multiprocessing
# ------------------------------
def download_with_multiprocessing():
    with mp.get_context("spawn").Pool() as pool:
        results = pool.starmap(
            download_image,
            zip(IMAGES, [f"mp_{i}.jpg" for i in range(len(IMAGES))])
        )
    return results

# ------------------------------
# Asyncio
# ------------------------------
async def async_download_image(session, url, filename):
    async with session.get(url) as resp:
        content = await resp.read()
        with open(filename, "wb") as f:
            f.write(content)
    return filename

async def download_with_asyncio():
    async with aiohttp.ClientSession() as session:
        tasks = [
            async_download_image(session, url, f"async_{i}.jpg")
            for i, url in enumerate(IMAGES)
        ]
        return await asyncio.gather(*tasks)

# ------------------------------
# Medir tiempo + mostrar imágenes
# ------------------------------
def mostrar_imagenes(result):
    fig, axes = plt.subplots(1, len(result), figsize=(6*len(result), 6))
    if len(result) == 1:
        axes = [axes]
    for ax, file in zip(axes, result):
        img = Image.open(file)
        ax.imshow(img)
        ax.axis("off")
        ax.set_title(file)
    plt.show()

def medir_tiempo(func, is_async=False):
    start = time.perf_counter()
    if is_async:
        try:
            result = asyncio.run(func())
        except RuntimeError:  # <-- Jupyter ya tiene loop
            import nest_asyncio
            nest_asyncio.apply()
            result = asyncio.run(func())
    else:
        result = func()
    end = time.perf_counter()

    print(f"\n{func.__name__} terminó en {end - start:.2f} segundos")
    mostrar_imagenes(result)
    return result

# ------------------------------
if __name__ == "__main__":
    print("Comparación de concurrencia:\n")
    medir_tiempo(download_with_multiprocessing)
    medir_tiempo(download_with_threads)
    medir_tiempo(download_with_asyncio, is_async=True)
