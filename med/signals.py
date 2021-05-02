from django.db.models.signals import post_save
from .models import Equipment 
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw


@receiver(post_save, sender=Equipment)
def save_qrcode(sender, instance, created, **kwargs):
    if created:
        qr = qrcode.QRCode(
                        version=1,
                        box_size=10,
                        border=5)
        qr.add_data(f'https://hospital-msm.herokuapp.com/workflow/submit-ticket-id/{instance.id}')
        qr.make(fit=True)
        qrcode_img = qr.make_image(fill='black', back_color='white')
        canvas = Image.new('RGB', (qrcode_img.pixel_size, qrcode_img.pixel_size), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qrcode-{instance.name}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        instance.qr_code.save(fname, File(buffer))
        canvas.close()
    