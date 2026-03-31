from PyPDF2 import PdfReader, PdfWriter, Transformation
from pyppeteer import launch
from PIL import Image
from fpdf import FPDF
import os
import asyncio
from reportlab.pdfgen import canvas
from io import BytesIO

class PDFConverter:
    def __init__(self):
        pass

    async def convert_png_to_pdf(self, png_file_path, dpi=300):
        image = Image.open(png_file_path).convert('RGB')
        pdf = FPDF(unit="pt", format=[image.width * dpi / 72, image.height * dpi / 72])
        pdf.set_compression(False)
        pdf.add_page()
        pdf.image(png_file_path, 0, 0, image.width * dpi / 72, image.height * dpi / 72)
        pdf_file_path = os.path.splitext(png_file_path)[0] + '.pdf'
        pdf.output(pdf_file_path, "F")
        os.remove(png_file_path)

    async def scale_pdf(self, name):
        reader = PdfReader(f'Front/static/document/PDF/{name}.pdf')
        page = reader.pages[0]
        page_width = page.mediabox.upper_right[0]
        page_height = page.mediabox.upper_right[1]
        scale_x = page_width / page.mediabox.width
        scale_y = page_height / page.mediabox.height
        scale_factor = min(scale_x, scale_y)
        op = Transformation().scale(sx=scale_factor, sy=scale_factor)
        page.add_transformation(op)
        writer = PdfWriter()
        writer.add_page(page)
        writer.write(f"Front/static/document/PDF/{name}.pdf")

    async def add_hyperlink_to_pdf(self, pdf, url, text, font_size, font):
        reader = PdfReader(open(pdf, "rb"))
        output = PdfWriter()
        packet = BytesIO()
        first_page = reader.pages[0]
        width, height = first_page.mediabox.upper_right
        can = canvas.Canvas(packet, pagesize=(width, height))
        x = 1250
        y = 200
        can.setFont(font, font_size)
        can.drawString(x, y, text)
        link_width = can.stringWidth(text, font, font_size)
        can.linkURL(url, (x, y, x + link_width, y + font_size), thickness=0)
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        for i, page in enumerate(reader.pages):
            if i == 0:
                page.merge_page(new_pdf.pages[0])
            output.add_page(page)
        with open(pdf, "wb") as outputStream:
            output.write(outputStream)

    async def screenshot_chromium(self, id_user, key):
        name = 'cp_info'
        text = "Start CsortBot"
        font_size = 120
        font = 'Helvetica'
        url = "https://t.me/MowlerMyprog_bot"
        
        browser = await launch({'args': ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080']})
        try:
            page = await browser.newPage()
            await page.setViewport({'width': 400, 'height': 1000, 'deviceScaleFactor': 2})
            await page.goto(f'https://csort-news.ru/offer/PDF?tg_id={id_user}&keyCP={key}', {'waitUntil': 'networkidle0'})
            screenshot_path = f'Front/static/document/PDF/{name}.png'
            await page.screenshot({'path': screenshot_path, 'fullPage': True, 'type': 'png'})
            await self.convert_png_to_pdf(screenshot_path)
            await self.add_hyperlink_to_pdf(f'Front/static/document/PDF/{name}.pdf', url, text, font_size, font)
            await self.scale_pdf(name)
        finally:
            await browser.close()
        return  f'Front/static/document/PDF/{name}.pdf'



