import base64
import io
from django.core.files import File


def b64tofile(b64):
    file_data = b64.split(',')
    if file_data:
        ext = file_data[0].split(';')[0].split('/')[1]
        file = io.BytesIO(base64.b64decode(
            file_data[1]))
        dj_file = File(file)
        return 'image.'+ext, dj_file
