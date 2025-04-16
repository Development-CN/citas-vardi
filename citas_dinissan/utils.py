import json
from typing import List
from asgiref.sync import async_to_sync
import pprint

import requests as api
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import ScheduledTask

COREAPI_URL = settings.COREAPI_MENSAJES
HEADERS = {"Content-Type": "application/json"}

from dataclasses import dataclass
from datetime import datetime


@dataclass
class InformacionCita:
    # Cliente
    cliente_cedula: str
    cliente_nombre: str
    cliente_primer_apellido: str
    cliente_segundo_apellido: str
    cliente_celular: str
    cliente_telefono_fijo: str
    cliente_correo: str
    cliente_direccion: str
    cliente_tipo_relacion: str
    cliente_medio_confirmacion: str

    # Vehículo
    vehiculo_placa: str
    vehiculo_ultimo_km: str
    vehiculo_km_actual: str
    vehiculo_vin: str
    ano: int
    vehiculo_descripcion_modelo_tasa: str
    vehiculo_codigo_modelo_tasa: str
    vehiculo_color: str
    vehiculo_fecha_vencimiento_soat: str
    vehiculo_fecha_vencimiento_tecnomecanica: str

    # Servicio
    motivo_ingreso: str
    tipo_revision_select: List[str]
    tipos_revision: str
    tipos_revision_info: str
    try:
        precios: List[str]
    except:
        precios: str
    comentarios: str

    # Punto de servicio
    ciudad: str
    punto_servicio: str
    cita_fecha: str
    id_asesor: str
    cita_hora: str

    habeas_data: str = False
    propietario_vehiculo: str = False

    id_sesion: str = False

    username: str = None

    @property
        

    def dinissan_data(self) -> dict:
        lista_motivo_ingreso = []
        tipos_revision_info = list(self.tipos_revision_info)
        print("tipos_revision_info")
        print(tipos_revision_info)
        try:
            tipos_revision_info.remove('{')
        except:
            pass
        print(tipos_revision_info)
        for motivo_ingreso in tipos_revision_info:
            motivo_ingreso = json.loads(motivo_ingreso)
            lista_motivo_ingreso.append({
            "grupo": f"{motivo_ingreso['servicio_categoria']}",
            "paquete": f"{motivo_ingreso['servicio_codigo']}"
                })
            
        print("lista_motivo_ingreso")
        print(lista_motivo_ingreso)
        
        try:
            fecha_soat = datetime.strptime(self.vehiculo_fecha_vencimiento_soat[0], "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            fecha_soat = ""
        try:
            fecha_tecn = datetime.strptime(self.vehiculo_fecha_vencimiento_tecnomecanica[0], "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            fecha_tecn = ""

        try:
            precios = self.precios[0]
        except:
            precios = self.precios

        data = {
            "placa": self.vehiculo_placa[0].strip().upper(),
            "cedula": self.cliente_cedula[0].strip(),
            "nombres": self.cliente_nombre[0].strip().upper(),
            "apellidos": self.cliente_primer_apellido[0].strip().upper()
            + " "
            + self.cliente_segundo_apellido[0].strip().upper(),
            "celular": self.cliente_celular[0].strip(),
            "correo": self.cliente_correo[0].strip(),
            "direccion": self.cliente_direccion[0].strip(),
            "fechaVencimientoSoat": fecha_soat,
            "fechaVencimientoTecn": fecha_tecn,
            "tipoRelacion": self.cliente_tipo_relacion[0],
            "mismoPropietario": True if self.propietario_vehiculo else False,
            "tratmientoDatos": True if self.habeas_data else False,
            "puntoServicio": self.punto_servicio[0],
            "fechaHoraCita": datetime.strptime(self.cita_fecha[0] + " " + self.cita_hora[0], "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%YT%H:%M:%S"),
            "asesor": self.id_asesor[0],
            "motivoPrincipal": self.motivo_ingreso[0],
            "motivoSecundario": self.tipos_revision_info[0],
            "observaciones": self.comentarios[0],
            "precio": precios,
            "medioConfirmacion": self.cliente_medio_confirmacion[0],
            "usuario": self.username,
            "envioTercero": True,
            "listGrupoPaqueteDTO": lista_motivo_ingreso,
            "descripcionModeloTasa": self.vehiculo_descripcion_modelo_tasa[0].strip()
        }
        return data


class NotificacionCorreo:
    def __init__(
        self, direccion_email=None, titulo=None, mensaje=None, cita=None, asesor=None, servicios=None, preview=None
    ):
        self.direccion_email = direccion_email
        self.mensaje = mensaje
        self.context = {
            # INFORMACION GENERICA
            "preview": preview,
            "titulo": titulo,
            "mensaje": mensaje,
            # ELEMENTOS UI
            "asesor": asesor,
            "cita": cita,
            "servicios": servicios,
            "logo": settings.LOGO,
        }
        self.html = self.render(self.context)

    def render(self, context):
        html = render_to_string("citas_dinissan/correo.html", context)
        return html

    def enviar(self):
        try:
            asunto_email = "Notificaciones Citas"
            email = EmailMessage(subject=asunto_email, body=self.html, to=self.direccion_email)
            email.content_subtype = "html"
            email.send(fail_silently=False)
            return True, self.mensaje
        except Exception as error:
            return False, self.mensaje


def get_data_api(request_body):
    if request_body.get("notificaciones-whatsapp") == "on":
        notificaciones = True
    else:
        notificaciones = False

    tiempo_total_motivo_ingreso = 0
    tipos_revision_info = list(request_body.getlist('tipos_revision_info'))
    print("tipos_revision_info")
    print(tipos_revision_info)
    try:
        tipos_revision_info.remove('{')
    except:
        pass
    print(tipos_revision_info)
    for motivo_ingreso in tipos_revision_info:
        motivo_ingreso = json.loads(motivo_ingreso)
        try:
            tiempo_motivo_ingreso = float(motivo_ingreso['servicio_tiempo'])
        except:
            tiempo_motivo_ingreso = 0.16
        tiempo_total_motivo_ingreso += tiempo_motivo_ingreso * 60
    print("tiempo_total_motivo_ingreso")
    print(tiempo_total_motivo_ingreso)

    parsed_data = {
        "id_asesor": request_body["id_asesor"],
        "no_placas": request_body["vehiculo_placa"],
        "fecha": request_body["cita_fecha"].replace("/", "-"),
        "cliente": request_body["cliente_nombre"] + " " + request_body["cliente_primer_apellido"] + " " + request_body["cliente_segundo_apellido"],
        "modelo": request_body["vehiculo_descripcion_modelo_tasa"],
        "color": request_body.get("vehiculo_color", "SIN COLOR"),
        "tiempo": int(tiempo_total_motivo_ingreso),
        "vin": request_body.get("vehiculo_vin", "00000000000000000"),
        "telefono": request_body["cliente_celular"],
        "hora_cita": request_body["cita_hora"],
        "correo": request_body["cliente_correo"],
        "whatsapp": notificaciones,
        "servicio": "",
        "kilometraje": int(request_body["vehiculo_km_actual"]),
        "id_agencia": int(request_body["punto_servicio"]),
        "observaciones": f"{json.loads(request_body['tipos_revision_info'])['servicio_nombre']} - {request_body['comentarios']}",
        "sede": "Bogota"
    }
    if not parsed_data["vin"]:
        parsed_data["vin"] = "00000000000000000"
    if not parsed_data["color"]:
        parsed_data["color"] = "SIN COLOR"

    try:
        parsed_data["ano"] = int(request_body["ano"])
    except (ValueError, TypeError):
        parsed_data["ano"] = 0
    return parsed_data

def get_data_api_dinissan(request_body, no_cita):
    if request_body.get("notificaciones-whatsapp") == "on":
        notificaciones = True
    else:
        notificaciones = False
    modelo_nombre = request_body["vehiculo_codigo_modelo_tasa"]
    print(datetime.strptime(request_body["cita_fecha"].replace("/", "-"), "%Y-%M-%d").isoformat(sep="T", timespec="minutes"))
    parsed_data = {
        "id_Concesionario": "0001",
        "id_Sucursal": "AA",
        "num_cita": str(no_cita),
        "fecha_cita": datetime.strptime(request_body["cita_fecha"].replace("/", "-"), "%Y-%M-%d").isoformat(sep="T", timespec="minutes"),
        "Hora_Recepcion": request_body["cita_hora"],
        "tipo_unidad": modelo_nombre,
        "cliente": request_body["cliente_nombre"] + request_body["cliente_primer_apellido"] + request_body["cliente_segundo_apellido"],
        "asesor": str(request_body["id_asesor"]),
        "id_asesor": str(request_body["id_asesor"]),
        "id_cliente": request_body["cliente_cedula"],
        "vin": request_body.get("vehiculo_vin", "00000000000000000"),
        "observaciones": "",
        "placas": request_body["vehiculo_placa"],
    }
    if not parsed_data["vin"]:
        parsed_data["vin"] = "00000000000000000"

    print("json tablero")
    print(parsed_data)
    return parsed_data

def whatsapp_citas(fase, telefono, datos_cita=None, mensaje=None):
    if fase == 0:
        mensaje = (
            f"{settings.AGENCIA}\n"
            + "Le recuerda que su cita ha quedado agendada.\n"
            + f"*Fecha:* {datos_cita['fecha']} \n"
            + f"*Hora:* {datos_cita['hora_cita']} \n"
            + f"*Asesor:* {str(datos_cita['asesor']).title()} \n"
        )
    elif fase == 1:
        mensaje = (
            f"{settings.AGENCIA}\n"
            + "Le recuerda que su cita ha sido reagendada.\n"
            + f"*Fecha:* {datos_cita['fecha']}\n"
            + f"*Hora:* {datos_cita['hora']}\n"
            + f"*Asesor:* {str(datos_cita['asesor']).title()}\n"
        )
    elif fase == 2:
        mensaje = ""

    data = {
        "phone": "52" + str(telefono),
        "body": mensaje,
    }
    try:
        post = api.post(url=COREAPI_URL, data=json.dumps(data), headers=HEADERS)
        if post.status_code == 200:
            print("CORE API: MENSAJE DE WHATSAPP ENVIADO")
        else:
            print("CORE API: ERROR")
    except Exception as error:
        print(error)


async def correo_citas(fase, direccion_correo, datos_cita=None, asesor=None, sede=None):

    template_context = {}

    asunto = "Seguimiento en linea"

    template_context["nombre_agencia"] = settings.AGENCIA
    template_context["cotizacion_url"] = f"http://{settings.DOMINIO}:{settings.PUERTO}/tracker/login/"
    template_context["telefono_agencia"] = ""
    template_context["privacy_url"] = settings.AVISO_PRIVACIDAD
    template_context["logo"] = settings.LOGO

    if datos_cita:
        template_context["cita"] = datos_cita
    if datos_cita:
        template_context["primer_nombre"] = datos_cita["cliente"].split()[0]
    if asesor:
        template_context["asesor"] = asesor
    if sede:
        template_context["sede"] = sede

    if fase == 0:
        template_context["notif"] = True
        # asunto = "Su cita ha quedado agendada"

    html_content = render_to_string("citas_dinissan/correo_notificacion.html", template_context)

    client_mail = direccion_correo

    try:
        print("correo1")
        email = EmailMessage(subject=f"{settings.AGENCIA} | {asunto}", body=html_content, to=[client_mail])
        email.content_subtype = "html"
        print("correo2")
        email.send()
        print("correo3")

        print("CORREO ENVIADO")
    except Exception as error:
        print("error")
        print(error)



def recordatorio_citas(fase, direccion_correo, datos_cita=None, asesor=None, sede=None, schedule_id=None):
    # Actualiza el estado de la tarea
    if schedule_id:
        ScheduledTask.objects.filter(id=schedule_id).update(status='executing')

    template_context = {}

    asunto = "Recordatorio de cita"

    template_context["nombre_agencia"] = settings.AGENCIA
    template_context["cotizacion_url"] = f"http://{settings.DOMINIO}:{settings.PUERTO}/tracker/login/"
    template_context["telefono_agencia"] = ""
    template_context["privacy_url"] = settings.AVISO_PRIVACIDAD
    template_context["logo"] = settings.LOGO

    if datos_cita:
        template_context["cita"] = datos_cita
        template_context["primer_nombre"] = datos_cita["cliente"].split()[0]
    if asesor:
        template_context["asesor"] = asesor
    if sede:
        template_context["sede"] = sede

    if fase == 0:
        template_context["notif"] = True

    html_content = render_to_string("citas_dinissan/correo_notificacion.html", template_context)
    client_mail = direccion_correo

    try:
        print("correo1")
        email = EmailMessage(subject=f"{settings.AGENCIA} | {asunto}", body=html_content, to=[client_mail])
        email.content_subtype = "html"
        print("correo2")
        email.send()
        print("correo3")

        if schedule_id:
            ScheduledTask.objects.filter(id=schedule_id).update(
                status='completed', result='Correo enviado correctamente'
            )
        print("CORREO ENVIADO")
    except Exception as error:
        print("error")
        print(error)
        if schedule_id:
            ScheduledTask.objects.filter(id=schedule_id).update(status='error', error=str(error))


async def correo_cancelar(fase, direccion_correo, datos_cita=None, asesor=None, sede=None):
    template_context = {}

    template_context["asunto"] = "Seguimiento en linea"
    template_context["nombre_agencia"] = settings.AGENCIA
    template_context["cotizacion_url"] = f"http://{settings.DOMINIO}:{settings.PUERTO}/tracker/login/"
    template_context["telefono_agencia"] = ""
    template_context["privacy_url"] = settings.AVISO_PRIVACIDAD
    template_context["logo"] = settings.LOGO

    if datos_cita:
        template_context["cita"] = datos_cita
    if datos_cita:
        template_context["primer_nombre"] = datos_cita.cliente.split()[0]
    if asesor:
        template_context["asesor"] = asesor
    if sede:
        template_context["sede"] = sede

    if fase == 0:
        template_context["notif"] = True
        asunto = "Su cita ha quedado cancelada"

    html_content = render_to_string("citas_dinissan/correo_cancelar.html", template_context)

    client_mail = direccion_correo

    try:
        email = EmailMessage(subject=f"{settings.AGENCIA} | {asunto}", body=html_content, to=[client_mail])
        email.content_subtype = "html"
        email.send()

        print("CORREO ENVIADO")
    except Exception as error:
        print("error")
        print(error)
