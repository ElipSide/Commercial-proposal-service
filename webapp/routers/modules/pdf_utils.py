import asyncio
from concurrent.futures import ThreadPoolExecutor
from weasyprint import HTML

# Максимум 2 потока — достаточно для генерации без перегрузки CPU
_pdf_executor = ThreadPoolExecutor(max_workers=5)

URL = "http://localhost:8000/off_bot"


async def convert_html_to_pdf_kp(html_content: str, output_filename: str, text_bottom: str):
    css_template = f"""
        <style>
            @page {{
                @bottom-left {{
                    content: "";
                    background-image: url("{URL}/static/img/logo_1.png");
                    background-size: 120px 28px;
                    width: 120px;
                    height: 28px;
                    background-repeat: no-repeat;
                }}
                @bottom-center {{
                    content: "{text_bottom}";
                    font-family: 'Ubuntu', sans-serif;
                    font-size: 12px;
                    margin-bottom: 50px;
                }}
                @bottom-right {{
                    content: counter(page);
                    font-family: 'Ubuntu', sans-serif;
                    font-size: 14px;
                    margin-bottom: 50px;
                }}
            }}
        </style>
        {html_content}
    """

    html = HTML(string=css_template)

    loop = asyncio.get_running_loop()
    # PDF-рендеринг уходит в пул потоков (не блокирует сервер)
    await loop.run_in_executor(_pdf_executor, html.write_pdf, output_filename)
