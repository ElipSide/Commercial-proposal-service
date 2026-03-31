import asyncio
import json
import os
import aiohttp
from concurrent.futures import ThreadPoolExecutor

url_download_base = "https://csort-tech.ru/report/"
url_generate = url_download_base + "generate_reports/"

# ограничиваем количество фонов потоков (чтобы не перегружать сервер)
_executor = ThreadPoolExecutor(max_workers=2)

async def _generate_pdf_request(product: str) -> str | None:
    if not product:
        return None

    data = {'products': [product], 'range_date': ["60 дней"]}
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url_generate, headers=headers, data=json.dumps(data), timeout=30) as resp:
                if resp.status == 200:
                    report_data = await resp.json()
                    pdf_links = report_data.get('pdf_reports', [])
                    if not pdf_links:
                        print(f"[CreatePDF] PDF-ссылки отсутствуют для {product}")
                        return None

                    link = pdf_links[0]
                    download_url = url_download_base + link
                    print(f"[CreatePDF] Ссылка на PDF: {download_url}")
                    return download_url
                else:
                    text = await resp.text()
                    print(f"[CreatePDF] Ошибка {resp.status}: {text}")
        except Exception as e:
            print(f"[CreatePDF] Ошибка при обращении к API: {e}")

    return None


def _run_sync_generate(product: str):
    asyncio.run(_generate_pdf_request(product))


async def createPDF(product: str, background: bool = True) -> str | None:
    if not product:
        return None

    if background:
        loop = asyncio.get_running_loop()
        # выполняем в отдельном потоке — полностью независимом от FastAPI event loop
        loop.run_in_executor(_executor, _run_sync_generate, product)
        print(f"[CreatePDF] Фоновая генерация PDF для {product} запущена")
        return None
    else:
        return await _generate_pdf_request(product)
