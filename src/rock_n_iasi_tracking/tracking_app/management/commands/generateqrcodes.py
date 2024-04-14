from django.core.management.base import BaseCommand, CommandError

from tracking_app.models import QrCodeId
from PIL import Image, ImageOps
import qrcode
from uuid import uuid4

from pathlib import Path

class Command(BaseCommand):
    help = 'Generates a4 size images with unique uuid4 qrcodes'

    def add_arguments(self, parser):
        parser.add_argument('pages', type=int)

    def handle(self, *args, **options):
        nr_pages = options['pages']

        qr_border = 5
        qr_width = 500 - qr_border
        qr_height = 500 - qr_border

        page_width = 2480
        page_height = 3508

        for k in range(nr_pages):
            page = Image.new('RGB', (page_width, page_height), (255, 255, 255))
            
            for i in range(int(page_height/qr_height)):
                for j in range(int(page_width/qr_width)):
                    qrcodeid = QrCodeId.objects.create()
                    qr_img = qrcode.make(qrcodeid.id)
                    qr_img = qr_img.resize((qr_width, qr_height))
                    qr_img = ImageOps.expand(qr_img, border=qr_border, fill='black')

                    page.paste(qr_img, (j * qr_width, i * qr_height))
            page.save('E:\qrcodes\%s.png'%k)
