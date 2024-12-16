import base64
import json
import os
from pathlib import Path

import numpy as np
import requests as api
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import Group, User
from django_drf_filepond.models import TemporaryUpload
from PIL import Image

from citas_dinissan.models import ActividadesCitas
from citas_dinissan.models import CitasStatusCita as StatusCita

BASE_DIR: Path = settings.BASE_DIR
MEDIA_DIR: Path = settings.MEDIA_ROOT
AUTH_DIR: Path = MEDIA_DIR / "auth"
COREAPI_URL = settings.COREAPI_MENSAJES

if not os.path.exists(AUTH_DIR):
    os.makedirs(AUTH_DIR)


def tracker_login(request, no_placas):
    # REVISAR SI EL CLIENTE TIENE CITA
    print(no_placas)
    try:
        cita = ActividadesCitas.objects.filter(no_placas=no_placas).order_by("-fecha_hora_fin").first()
    except Exception as e:
        print(e)
        cita = None

    try:
        status_cita = StatusCita.objects.get(no_cita=cita.no_cita)
    except Exception as e:
        print(e)
        status_cita = StatusCita.objects.none()

    if cita:
        # REVISAR SI EL CLIENTE ESTA REGISTRADO
        try:
            cliente = User.objects.get(username=cita.no_cita)
        except Exception as e:
            print(e)
            group = Group.objects.get_or_create(name="cliente")[0]
            cliente = User.objects.create(
                username=cita.no_cita,
                first_name=cita.cliente,
                email=cita.correo,
                is_staff=False,
            )
            cliente.groups.add(group)

        if cliente and not status_cita:
            login(request, cliente)
            return True

        if cliente and not status_cita.fecha_hora_fin_cancelacion:
            login(request, cliente)
            return True
        else:
            return False


def guardar_base_64(base_64_str, no_unico, razon):
    THRESHOLD = 100
    DIST = 5

    data = base_64_str[22:].encode()

    with open(os.path.join(AUTH_DIR, "tmp.png"), "wb") as tmp:
        tmp.write(base64.decodebytes(data))

    img_buffer = Image.open(os.path.join(AUTH_DIR, "tmp.png")).convert("RGBA")
    arr = np.array(np.asarray(img_buffer))

    r, g, b, a = np.rollaxis(arr, axis=-1)

    mask = (
        (r > THRESHOLD)
        & (g > THRESHOLD)
        & (b > THRESHOLD)
        & (np.abs(r - g) < DIST)
        & (np.abs(r - b) < DIST)
        & (np.abs(g - b) < DIST)
    )
    arr[mask, 3] = 0
    img_buffer = Image.fromarray(arr, mode="RGBA")
    img_buffer.save(os.path.join(AUTH_DIR, f"{no_unico}-{razon}.png"))
    os.remove(os.path.join(BASE_DIR, "media", "auth", "tmp.png"))


def save_filepond(saving_list):
    """SAVES FILEPOND UPLOADS

    Args:
        saving_list (LIST): FILE'S SERVER ID LIST
    """
    elements = TemporaryUpload.objects.filter(upload_id=saving_list)
    for element in elements:
        os.rename(element.get_file_path(), os.path.join(MEDIA_DIR, element.upload_name))
        element.delete()
        print("FILEPOND ACTUALIZADO")


def enviar_whatsapp(prefijo, telefono, mensaje):
    HEADERS = {"Content-Type": "application/json"}
    DATA = {
        "phone": f"{prefijo}{telefono}",
        "body": mensaje,
    }
    try:
        post = api.post(url=COREAPI_URL, data=json.dumps(DATA), headers=HEADERS)
        if post.status_code == 200:
            return "CORE API: MENSAJE DE WHATSAPP ENVIADO"
        else:
            return "CORE API: ERROR"
    except Exception as e:
        return e
