import asyncio
import json
from datetime import datetime, date, timedelta

import requests as api
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateView
from django_q.models import Schedule
from django_q.tasks import schedule
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import *
from .serializers import AgenciaSerializer, AsesorSerializer
from .utils import (
    InformacionCita,
    NotificacionCorreo,
    correo_citas,
    correo_cancelar,
    get_data_api,
    get_data_api_dinissan,
    whatsapp_citas,
)

CITA_CREAR = settings.CITAS_TABLEROAPI + "/api/nueva_cita/"
CITA_BORRAR = settings.CITAS_TABLEROAPI + "/api/cancelar_cita/"
CITA_REAGENDAR = settings.CITAS_TABLEROAPI + "/api/reagendar_cita/"
DISPONIBILIDAD_ASESOR = settings.CITAS_TABLEROAPI + "/api/disponibilidad_asesor"

URL_DATOS_CLIENTE = settings.COREAPI_DATOS_CLIENTE + "/api/v1.2/tablero/info_crm/"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# Define dinámicamente si la clase incluye LoginRequiredMixin o no
if settings.LOGIN_REQUIRED:
    BaseClass = type('BaseClass', (LoginRequiredMixin, TemplateView), {})
else:
    BaseClass = TemplateView


class ClienteNuevaCita(BaseClass):
    template_name = 'citas_dinissan/cliente_nueva_cita.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = settings.AGENCIA
        context["settings"] = settings

        context["ciudades"] = AgenciaTablero.objects.all().values_list("ciudad", flat=True).distinct()

        try:
            id_sesion = Log.objects.all().last().id_sesion + 1
        except:
            id_sesion = 1

        context["motivos_ingreso"] = MotivoIngreso.objects.all()
        context["id_sesion"] = id_sesion
        return context

    def post(self, request, *args, **kwargs):
        r = request.POST
        if r.get("validacion_placas", None):
            cita = ActividadesCitas.objects.filter(no_placas=r["placas"]).order_by("id").last()
            if cita:
                if cita.id_estado in [1, 2, 4]:
                    return HttpResponse(status=404)
                else:
                    return HttpResponse(status=200)
            else:
                return HttpResponse(status=200)

        if r.get("logs", None):
            try:
                log = Log.objects.get(id_sesion=r.get("id_sesion", None))
            except:
                log = Log.objects.create(id_sesion=r.get("id_sesion", None), fecha=date.today(), hora=datetime.now())
            
            print(r)
            print(r.get("tipos_revision_info", None))
            print(r.get("cita_fecha", None))
            if r.get("ip_address", None):
                log.ip_address = r.get("ip_address", None)
            if r.get("vehiculo_placa", None):
                log.placa = r.get("vehiculo_placa", None)
            if r.get("cliente_cedula", None):
                log.cedula = r.get("cliente_cedula", None)
            if r.get("cliente_nombre", None):
                log.nombre = r.get("cliente_nombre", None)
            if r.get("cliente_primer_apellido", None):
                log.primer_apellido = r.get("cliente_primer_apellido", None)
            if r.get("cliente_segundo_apellido", None):
                log.segundo_apellido = r.get("cliente_segundo_apellido", None)
            if r.get("cliente_celular", None):
                log.celular = r.get("cliente_celular", None)
            if r.get("cliente_telefono_fijo", None):
                log.telefono_fijo = r.get("cliente_telefono_fijo", None)
            if r.get("cliente_correo", None):
                log.correo = r.get("cliente_correo", None)
            if r.get("cliente_direccion", None):
                log.direccion = r.get("cliente_direccion", None)
            if r.get("cliente_tipo_relacion", None):
                log.tipo_de_relacion = r.get("cliente_tipo_relacion", None)
            if r.get("medio_de_confirmacion", None):
                log.medio_de_confirmacion = r.get("medio_de_confirmacion", None)
            if r.get("vehiculo_ultimo_km", None):
                log.ultimo_km = r.get("vehiculo_ultimo_km", None)
            if r.get("vehiculo_km_actual", None):
                log.km_actual = r.get("vehiculo_km_actual", None)
            if r.get("vehiculo_vin", None):
                log.vin = r.get("vehiculo_vin", None)
            if r.get("vehiculo_descripcion_modelo_tasa", None):
                log.descripcion_modelo_tasa = r.get("vehiculo_descripcion_modelo_tasa", None)
            if r.get("vehiculo_color", None):
                log.color = r.get("vehiculo_color", None)      
            if r.get("vehiculo_fecha_de_vencimiento_soat", None):
                log.fecha_de_vencimiento_soat = r.get("vehiculo_fecha_de_vencimiento_soat", None)
            if r.get("vehiculo_fecha_de_vencimiento_tecnomecanica", None):
                log.fecha_de_vencimiento_tecnomecanica = r.get("vehiculo_fecha_de_vencimiento_tecnomecanica", None)    
            if r.get("motivo_ingreso", None):
                log.motivo_de_ingreso = r.get("motivo_ingreso", None)    
            if r.get("tipos_revision_info", None):
                log.tipo_de_revision_o_paquete = r.get("tipos_revision_info", None)
            if r.get("comentarios", None):
                log.comentarios = r.get("comentarios", None)    
            if r.get("ciudad", None):
                log.ciudad = r.get("ciudad", None)
            if r.get("punto_servicio", None):
                log.punto_de_servicio = r.get("punto_servicio", None)
            if r.get("cita_fecha", None):
                log.fecha_cita = r.get("cita_fecha", None).replace("/", "-")
            if r.get("cita_hora", None):
                log.hora_cita = r.get("cita_hora", None)

            log.fecha = date.today()
            log.hora = datetime.now()

            print(request.user)

            if settings.LOGIN_REQUIRED:
                log.user = request.user
            log.save()
            return JsonResponse({"success": True}, safe=False)


class CitasServices(APIView):
    def post(self, request: Request, *args, **kwargs):
        if request.data.get("punto_servicio"):
            print("Obtencion de agencias")
            print(request.data)

            ciudad = request.data.get("ciudad")
            agencias = AgenciaTablero.objects.filter(Q(ciudad__icontains=ciudad) | Q(ciudad__icontains=ciudad.strip()))
            serializer = AgenciaSerializer(agencias, many=True)

            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.data.get("asesores"):
            print("Obtencion de asesores")
            print(request.data)

            asesores = VCitasUsuarios.objects.filter(id_agencia=request.data.get("id_agencia"), activo=True)
            serializer = AsesorSerializer(asesores, many=True)

            print(asesores)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.data.get("disponibilidad"):
            print("Obtencion de disponibilidad")
            print(request.data)

            api_tablero = AgenciaTablero.objects.get(id_agencia=request.data.get("id_agencia")).url_api_tablero
            endpoint = api_tablero + "/api/disponibilidad_asesor"

            print("URL a consultar:")
            print(endpoint)

            print("Data a enviar:")
            print({"id_asesor": request.data.get("id_asesor"), "fecha": request.data.get("fecha")})

            response_disponibilidad = api.get(
                endpoint,
                json={"id_asesor": str(request.data.get("id_asesor")), "fecha": request.data.get("fecha")},
                headers=HEADERS,
            )

            print("Respuesta tablero:")
            print(response_disponibilidad.text)

            data = response_disponibilidad.json()
            disponibilidad = []
            for element in data:
                disponibilidad.append(element["hora"])

            print(disponibilidad)
            return Response(disponibilidad, status=status.HTTP_200_OK)


class DinissanServices(APIView):
    def post(self, request: Request, *args, **kwargs):
        response_token = api.post(
            "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/token",
            headers={"usuario": "Capnet", "clave": "a8876816b9b27e0927b9653005d96dac"},
        )
        token = response_token.text
        print("hola")
        print(token)

        if request.data.get("info_cliente"):
            print("hola1")

            # API Vardi
            response_info_vardi_token = api.post(
                "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/token",
                headers={"clave": "a8876816b9b27e0927b9653005d96dac", "usuario": "Capnet"},
            )
            token_vardi = response_info_vardi_token.text

            response_info_cliente = api.post(
                "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/infoVehiculoCliente",
                json={"placa": request.data["placa"], "cedula": request.data["cedula"]},
                headers={"token": token_vardi, "tenant": "4"},
                timeout=30  # Tiempo de espera en segundos
            )
            print("response_info_cliente")
            print(response_info_cliente)
            print(response_info_cliente.text)

            # API Mazda
            if settings.API_MAZDA:

                response_token = api.post(
                    "https://dm-us.informaticacloud.com/authz-service/oauth/token?grant_type=client_credentials",
                    auth=HTTPBasicAuth("3hN97ItSfCTguHjruDOMKF", "316L2sIdL")
                )
                token = response_token.json()["access_token"]

                print("tiempo para api mazda")

                try:
                    response_plate = api.post(
                        "https://apigw-pod1.dm-us.informaticacloud.com/t/8dbkbsgxnq1hgifvkspnoc.com/MCOL_03_VINES_INTEGRACION_Process",
                        headers={'Authorization': f'Bearer {token}'},
                        data={"Placa":request.data["placa"]},
                        timeout=70  # Tiempo de espera en segundos
                    )
                except:
                    response_plate = "Timeout de Mazda excedido"

                print("response_plate")
                print(response_plate)

            try:
                info_response_plate = response_plate.json()["EspecificacionVehiculo"]
                print(info_response_plate)

                response = {
                    "ano": info_response_plate["anioModelo"],
                    "vin": info_response_plate["vin"],
                    "color": info_response_plate["color"],
                }

                try:

                    dato_sales_force = DatosSalesForce.objects.get(placa=info_response_plate["placa"])
                    dato_sales_force.vin=info_response_plate["vin"]
                    dato_sales_force.motor = info_response_plate["motor"]
                    dato_sales_force.codigoLinea = info_response_plate["codigoLinea"]
                    dato_sales_force.descripcionLinea = info_response_plate["descripcionLinea"]
                    dato_sales_force.opcion = info_response_plate["opcion"]
                    dato_sales_force.vis = info_response_plate["vis"]
                    dato_sales_force.codColor = info_response_plate["codColor"]
                    dato_sales_force.color = info_response_plate["color"]
                    dato_sales_force.version = info_response_plate["version"]
                    dato_sales_force.identificadorProducto = info_response_plate["identificadorProducto"]
                    dato_sales_force.anioModelo = info_response_plate["anioModelo"]
                    dato_sales_force.servicio = info_response_plate["servicio"]
                    dato_sales_force.fechaEntrega = info_response_plate["fechaEntrega"]
                    dato_sales_force.fechaMatricula = info_response_plate["fechaMatricula"]
                    dato_sales_force.ciudadPlaca = info_response_plate["ciudadPlaca"]
                    dato_sales_force.codConcesionarioVendedor = info_response_plate["codConcesionarioVendedor"]
                    dato_sales_force.ConcesionarioVendedor = info_response_plate["ConcesionarioVendedor"]
                    dato_sales_force.campaniaSeguridadPendiente = info_response_plate["campaniaSeguridadPendiente"]
                    dato_sales_force.save()

                except:

                    DatosSalesForce.objects.create(
                        vin=info_response_plate["vin"],
                        placa=info_response_plate["placa"],
                        motor=info_response_plate["motor"],
                        codigoLinea=info_response_plate["codigoLinea"],
                        descripcionLinea=info_response_plate["descripcionLinea"],
                        opcion=info_response_plate["opcion"],
                        vis=info_response_plate["vis"],
                        codColor=info_response_plate["codColor"],
                        color=info_response_plate["color"],
                        version=info_response_plate["version"],
                        identificadorProducto=info_response_plate["identificadorProducto"],
                        anioModelo=info_response_plate["anioModelo"],
                        servicio=info_response_plate["servicio"],
                        fechaEntrega=info_response_plate["fechaEntrega"],
                        fechaMatricula=info_response_plate["fechaMatricula"],
                        ciudadPlaca=info_response_plate["ciudadPlaca"],
                        codConcesionarioVendedor=info_response_plate["codConcesionarioVendedor"],
                        ConcesionarioVendedor=info_response_plate["ConcesionarioVendedor"],
                        campaniaSeguridadPendiente=info_response_plate["campaniaSeguridadPendiente"],
                    )

            except:
                response = {
                    "ano": "",
                    "vin": "",
                    "color": "",
                }

            print("response")
            print(response)

            try:
                cita = ActividadesCitas.objects.filter(no_placas=request.data["placa"]).last()
                if cita.id_estado not in [3, 5, 6]:
                    return Response("tracker", status=status.HTTP_200_OK)
            except:
                pass

            if response_info_cliente.status_code == 200:
                info_cliente = response_info_cliente.json()
                info_cliente["ano"] = response["ano"]
                info_cliente["vin"] = response["vin"]
                info_cliente["color"] = response["color"]
                try:
                    info_cliente["observaciones"] = info_response_plate["campaniaSeguridadPendiente"]
                except:
                    info_cliente["observaciones"] = None
                return Response(info_cliente, status=status.HTTP_200_OK)
            else:
                info_cliente = "{}"
                return Response(info_cliente, status=status.HTTP_200_OK)


        if request.data.get("tipos_revision"):
            print("hola3")
            response_info_motivo_ingreso = api.post(
                "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/infoMotivoIngreso",
                json={
                    "chasis": request.data["chasis"],
                    "kilometraje": request.data["kilometraje"],
                    "categoria": int(request.data["categoria"]),
                },
                headers={"token": token, "tenant": "4"},
            )
            print(response_info_motivo_ingreso)

            if response_info_motivo_ingreso.ok:
                tipos_revision = response_info_motivo_ingreso.json()["listaPaquetes"]
            else:
                tipos_revision = "[]"
            print(tipos_revision)

            return Response(tipos_revision, status=status.HTTP_200_OK)


class Agenda(APIView):
    authentication_classes = [SessionAuthentication]  # ← ¡Importante!
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request: Request, *args, **kwargs):
        print("request")
        print(request)
        print(request.data)

        query_dict = dict(request.data)

        if 'precios' not in query_dict:
            query_dict['precios'] = ['']

        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = None
        
        print("username")
        print(username)

        query_dict['username'] = username

        informacion_cita = InformacionCita(**query_dict)

        # Token
        response_token = api.post(
            "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/token",
            headers={"usuario": "Capnet", "clave": "a8876816b9b27e0927b9653005d96dac"},
        )
        token = response_token.text
        print("hola3")
        print("token")
        print(response_token)
        print(token)

        # Información cita dinissan
        dinissan_data = informacion_cita.dinissan_data
        print("Informacion a enviar a Dinissan")
        print(dinissan_data)
        print(type(dinissan_data))

        r = request.POST

        servicios_peticion = r.getlist("tipos_revision_info")
        try:
            servicios_peticion.remove('{')
        except:
            pass

        servicios_nombres_list = []

        for servicio in servicios_peticion:
            servicio = json.loads(servicio)
            servicios_nombres_list.append(servicio["servicio_nombre"])

        # Concatenar los nombres con comas
        servicios_nombres_total = ', '.join(servicios_nombres_list)

        servicios_peticion2 = r.getlist("tipos_revision2")

        print("servicios_peticion2")
        print(servicios_peticion2)

        response_dinissan = api.post(
            "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/crearCitaWeb",
            json=dinissan_data,
            headers={"token": token, "tenant": "4"},
        )
        print("Respuesta Dinissan")
        print(response_dinissan)
        content_type = response_dinissan.headers.get('content-type', '')
        print(content_type)
        if 'text/html' in content_type:
            # Content is HTML, print the HTML content
            print(response_dinissan.text)
        elif 'application/json' in content_type:
            # Content is JSON, print the JSON content
            print(response_dinissan.json())
        else:
            # For other content types, print the binary content
            print(response_dinissan.content)
        print("hola4")
        print(response_dinissan.text)

        
        print("r")
        print(r)
        datos_cita = get_data_api(r, username)

        agencia_url = AgenciaTablero.objects.get(id_agencia=datos_cita["id_agencia"]).url_api_tablero
        sede = AgenciaTablero.objects.get(id_agencia=datos_cita["id_agencia"])

        CITA_CREAR = agencia_url + "/api/nueva_cita/"

        print("CITA_CREAR")
        print(CITA_CREAR)

        try:
            codigo = json.loads(response_dinissan.text)["codigo"]
        except:
            codigo = 200

        if codigo == 200:
            print(servicios_peticion)
            datos_cita["servicio"] = servicios_nombres_total
            print("datos_cita")
            print(datos_cita)
            try:
                no_cita_vardi = json.loads(response_dinissan.text)["numeroCita"]
            except:
                no_cita_vardi = None
            datos_cita["NumCita"] = no_cita_vardi
            print()
            post = api.post(url=CITA_CREAR, data=json.dumps(datos_cita), headers=HEADERS)
            print(post.text)
            if post.status_code == 200:
                respuesta = json.loads(post.text)
                no_cita = respuesta["details"]["no_cita"]
                id_hd = respuesta["details"]["id_hd"]
                datos_cita["NumCita"] = no_cita
            else:
                DATA_VARDI = {
                    "compania": "4",
                    "estadoCita": "cancelada",
                    "numeroCita": no_cita_vardi,
                    "puntoServicio": str(datos_cita["id_agencia"]),
                    "fechaHoraCita": timezone.datetime.combine(datos_cita["fecha"], datos_cita["hora_cita"]).isoformat(),
                    "idAsesor": datos_cita["id_asesor"],
                    "usuario": "Capnet",
                    "listGrupoPaqueteDTO": [
                        {
                        "grupo": 0,
                        "paquete": 0
                        }
                    ]
                }

                print("hola1")
                print(DATA_VARDI)
                response_info_cliente = api.post(
                    "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/modificarCitaWeb",
                    json=DATA_VARDI,
                    headers={"token": token, "tenant": "4"},
                )

                print(response_info_cliente)
                print(response_info_cliente.json())



            print(post.ok)
            if post.ok:
                print("CITA CREADA EN TABLERO")
                lista_servicios_nombres = []
                for servicio in servicios_peticion:
                    servicio = json.loads(servicio)
                    ActividadesCitasServicios.objects.create(no_cita=no_cita, servicio=servicio["servicio_nombre"], id_servicio=servicio["servicio_codigo"])
                    lista_servicios_nombres.append(servicio["servicio_nombre"])

            if post.ok:
                print("SERVICIOS CREADOS")
                respuesta = json.loads(post.text)
                separador = ", "
                nueva_cita = ActividadesCitas.objects.create(
                    no_cita=no_cita,
                    no_cita_vardi=no_cita_vardi,
                    id_hd=id_hd,
                    id_asesor=datos_cita["id_asesor"],
                    fecha_cita=datos_cita["fecha"].replace("/", "-"),
                    no_placas=datos_cita["no_placas"],
                    cliente=datos_cita["cliente"],
                    correo=datos_cita["correo"],
                    modelo_vehiculo=datos_cita["modelo"],
                    color_vehiculo=datos_cita["color"],
                    tiempo=datos_cita["tiempo"],
                    year_vehiculo=datos_cita["ano"],
                    vin=datos_cita["vin"],
                    telefono=datos_cita["telefono"],
                    hora_cita=datos_cita["hora_cita"],
                    status="0",
                    whatsapp=datos_cita["whatsapp"],
                    kilometraje=datos_cita["kilometraje"],
                    id_estado=1,
                    comentario=separador.join(lista_servicios_nombres),
                    id_agencia=datos_cita["id_agencia"],
                    observaciones=datos_cita["observaciones"]
                )
                print("CITA CREADA")

                try:
                    asesor = VCitasUsuarios.objects.get(cveasesor=datos_cita["id_asesor"]).nombre
                except Exception:
                    asesor = ""

                try:
                    sede = AgenciaTablero.objects.get(id_agencia=datos_cita["id_agencia"])
                except Exception:
                    sede = ""

                datos_cita["asesor"] = asesor

                CITA_CREAR_DINISSAN = "http://201.150.44.27:8985"
                datos_cita_dinissan = get_data_api_dinissan(r, no_cita)
                post_dinissan = api.post(url=CITA_CREAR_DINISSAN, data=json.dumps(datos_cita_dinissan), headers=HEADERS, auth=('S0022951509', 'Cpi@012@21User*'))
                print(post_dinissan.text)

                if datos_cita["whatsapp"]:
                    asyncio.run(whatsapp_citas(0, datos_cita["telefono"], datos_cita))

                asyncio.run(
                    correo_citas(
                        0,
                        datos_cita["correo"],
                        datos_cita=datos_cita,
                        asesor=asesor,
                        sede=sede,
                    )
                )

                function_name = 'citas_dinissan.utils.recordatorio_citas'
                parameters = {
                    "fase": 0,
                    "direccion_correo": datos_cita["correo"],
                    "datos_cita": datos_cita,
                    "asesor": asesor,
                    "sede": model_to_dict(sede),
                }

                fecha_hora_str = f"{datos_cita['fecha']} 11:00:00"
                run_at = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
                run_at = run_at - timedelta(days=1)
                run_at_qcluster = run_at - timedelta(hours=6)

                schedule_task = ScheduledTask.objects.create(
                    function_name=function_name,
                    parameters=parameters,
                    scheduled_date=run_at,
                    appointment=nueva_cita
                )

                schedule(
                    function_name,
                    0,
                    datos_cita["correo"],
                    datos_cita,
                    asesor,
                    model_to_dict(sede),
                    schedule_id=schedule_task.id,
                    next_run=run_at,
                    schedule_type='O',
                    repeats=4
                )

                # Correo al contact center para notificar la creación de la cita
                nueva_notificacion_correo = NotificacionCorreo(
                    "angiecastaneda.capnet@gmail.com",
                    titulo="Nueva cita creada",
                    mensaje="",
                    cita=nueva_cita,
                    asesor=asesor,
                    servicios="",
                )
                nueva_notificacion_correo.enviar()

                campanas_y_precios = "Fecha: " + datos_cita["fecha"].replace("/", "-") + ".<br>Hora: " + datos_cita["hora_cita"] + ".<br>Asesor: " + asesor + ".<br>Sede: " + sede.nombre + ".<br>Dirección: " + sede.ciudad + ".<br>Servicio: " + separador.join(lista_servicios_nombres) + ".<br>Placa: " + datos_cita["no_placas"]

                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]  # Toma la primera IP en la lista
                else:
                    ip = request.META.get('REMOTE_ADDR')

                try:
                    log = Log.objects.get(id_sesion=query_dict['id_sesion'][0])
                except:
                    log = Log.objects.create(id_sesion=query_dict['id_sesion'][0], fecha=date.today(), hora=datetime.now())
                
                if no_cita:
                    log.no_cita = no_cita
                if no_cita_vardi:
                    log.no_cita_vardi = no_cita_vardi
                if id_hd:
                    log.id_hd = id_hd

                log.save()

                return JsonResponse(campanas_y_precios, safe=False, status=200)

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


                return Response(status=status.HTTP_200_OK)
            if response_dinissan.ok:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print("JSONRESPONSE")
            return JsonResponse(json.loads(response_dinissan.text)["mensaje"] + ".<br>Lo invitamos a continuar con el agendamiento seleccionando otra fecha, hora o asesor dando click en el X", safe=False, status=400)


class ClienteCancelarCita(LoginRequiredMixin, TemplateView):
    login_url = "tracker_pro_login"
    template_name = "citas_dinissan/cliente_cancelar_cita.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = "Capital Network"
        context["settings"] = settings

        cliente = self.request.user
        no_cita = cliente.username

        if isinstance(no_cita, str):
            cita = ActividadesCitas.objects.get(no_cita=no_cita)
            context["fecha_hora_cita"] = str(cita.fecha_cita) + " " + str(cita.hora_cita)
            context["vin"] = cita.vin
        return context

    def post(self, request):
        if request.POST.get("cancelar_cita", None):
            cliente = request.user
            no_cita = cliente.username

            DATA = {"NumCita": int(no_cita)}

            cita = ActividadesCitas.objects.get(no_cita=no_cita)

            agencia_url = AgenciaTablero.objects.get(id_agencia=cita.id_agencia).url_api_tablero
            CITA_BORRAR = agencia_url + "/api/cancelar_cita/"

            print("CITA_BORRAR")
            print(CITA_BORRAR)

            post = api.post(url=CITA_BORRAR, data=json.dumps(DATA), headers=HEADERS)
            print(post.text)
            print(DATA)
            print(json.dumps(DATA))

            response_token = api.post(
                "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/token",
                headers={"usuario": "Capnet", "clave": "a8876816b9b27e0927b9653005d96dac"},
            )
            token = response_token.text
            print("hola")

            
            DATA_VARDI = {
                "compania": "4",
                "estadoCita": "cancelada",
                "numeroCita": cita.no_cita_vardi,
                "puntoServicio": str(cita.id_agencia),
                "fechaHoraCita": timezone.datetime.combine(cita.fecha_cita, cita.hora_cita).isoformat(),
                "idAsesor": cita.id_asesor,
                "usuario": "Capnet",
                "listGrupoPaqueteDTO": [
                    {
                    "grupo": 0,
                    "paquete": 0
                    }
                ]
            }


            print("hola1")
            print(DATA_VARDI)
            response_info_cliente = api.post(
                "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/modificarCitaWeb",
                json=DATA_VARDI,
                headers={"token": token, "tenant": "4"},
            )

            print(response_info_cliente)
            print(response_info_cliente.json())

            cita.status = 3
            cita.id_estado = 3
            cita.save()

            schedule_task = ScheduledTask.objects.get(appointment=cita)

            Schedule.objects.filter(kwargs__contains="{'schedule_id': " + str(schedule_task.id) + "}").delete()

            schedule_task.delete()

            if post.status_code == 200:
                update = CitasStatusCita.objects.get(no_cita=no_cita)
                update.fecha_hora_fin_cancelacion = datetime.now()
                update.save()
                logout(request)

                try:
                    update_cita = (
                        ActividadesCitas.objects.filter(no_cita=no_cita).order_by("-fecha_hora_fin").first()
                    )
                    update_cita.id_estado = 3
                    update_cita.save()


                    try:
                        sede = AgenciaTablero.objects.get(id_agencia=update_cita.id_agencia)
                    except Exception:
                        sede = ""


                    asesor = VCitasUsuarios.objects.filter(cveasesor=update_cita.id_asesor).first().nombre

                    asyncio.run(
                        correo_cancelar(
                            0,
                            update_cita.correo,
                            update_cita,
                            asesor=asesor,
                            sede=sede,
                        )
                    )

                    nuevo_correo = NotificacionCorreo(
                        direccion_email=update.correo,
                        titulo="Solicitud de cancelación de cita",
                        mensaje="Se ha solicitado la cancelación de la cita con los siguientes datos:",
                        cita=update_cita,
                        asesor=asesor,
                        preview="",
                    )
                    nuevo_correo.enviar()

                    # Correo al contact center para notificar la cancelación de la cita
                    nuevo_correo = NotificacionCorreo(
                        direccion_email=settings.CITAS_CORREOS_INTERNOS,
                        titulo="Solicitud de cancelación de cita",
                        mensaje="Se ha solicitado la cancelación de la cita con los siguientes datos:",
                        cita=update_cita,
                        asesor=asesor,
                        preview="",
                    )
                    nuevo_correo.enviar()
                except Exception as error:
                    print(error)

                return redirect("tracker_pro_login")


class ClienteReagendarCita(LoginRequiredMixin, TemplateView):
    login_url = "tracker_pro_login"
    template_name = "citas_dinissan/cliente_reagendar_cita.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = settings.AGENCIA
        context["lista_asesores"] = VCitasUsuarios.objects.filter(activo=True)
        context["settings"] = settings

        context["modelos"] = ListaItemsModelos.objects.all().values_list("nombre", flat=True)
        context["años"] = ListaItemsYears.objects.all().values_list("year", flat=True)

        cliente = self.request.user
        no_cita = cliente.username

        if isinstance(no_cita, str):
            cita = ActividadesCitas.objects.get(no_cita=no_cita)
            context["fecha_hora_cita"] = str(cita.fecha_cita) + " " + str(cita.hora_cita)

        return context

    def post(self, request):
        r = request.POST
        cliente = self.request.user
        no_cita = cliente.username

        DATA = {
            "no_cita": int(no_cita),
            "fecha": r["fecha"].replace("/", "-"),
            "hora": r["hora"],
            "id_asesor": r["id_asesor"],
        }
        print(DATA)

        cita = ActividadesCitas.objects.get(no_cita=no_cita)

        agencia_url = AgenciaTablero.objects.get(id_agencia=cita.id_agencia).url_api_tablero
        CITA_REAGENDAR = agencia_url + "/api/reagendar_cita/"

        post = api.post(url=CITA_REAGENDAR, data=json.dumps(DATA), headers=HEADERS)
        print(post.text)

        if post.status_code == 200:
            update = ActividadesCitas.objects.filter(no_cita=no_cita).first()
            update.fecha_cita = r["fecha"].replace("/", "-")
            update.hora_cita = r["hora"]
            update.id_asesor = r["id_asesor"]
            update.id_estado = 4
            update.save()

            datos_cita = {}
            datos_cita["fecha"] = update.fecha_cita
            datos_cita["hora"] = update.hora_cita
            datos_cita["no_placas"] = update.no_placas

            try:
                asesor = VCitasUsuarios.objects.get(cveasesor=update.id_asesor).nombre
            except Exception:
                asesor = ""

            # CORREO
            asyncio.run(
                correo_citas(
                    fase=0,
                    direccion_correo=cliente.email,
                    datos_cita=datos_cita,
                    asesor=asesor,
                )
            )

            function_name = 'citas_dinissan.utils.recordatorio_citas'
            parameters = {
                "fase": 0,
                "direccion_correo": cliente.email,
                "datos_cita": datos_cita,
                "asesor": asesor,
            }

            schedule_task = ScheduledTask.objects.get(appointment=update)

            Schedule.objects.filter(kwargs__contains="{'schedule_id': {schedule_task.id}}").delete()

            schedule_task.delete()

            fecha_hora_str = f"{r['fecha']} 11:00:00"
            run_at = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
            run_at = run_at - timedelta(days=1)

            schedule_task = ScheduledTask.objects.create(
                function_name=function_name,
                parameters=parameters,
                scheduled_date=run_at,
                appointment=update
            )

            schedule(
                function_name,
                0,
                datos_cita["correo"],
                datos_cita,
                asesor,
                schedule_id=schedule_task.id,
                next_run=run_at,
                schedule_type='O',
                repeats=4
            )

            # WHATSAPP
            if update.whatsapp:
                datos_cita["asesor"] = asesor
                whatsapp_citas(1, update.telefono, datos_cita)

            # Notificación de cita reagendada al contact center
            nueva_notificacion_correo = NotificacionCorreo(
                settings.CITAS_CORREOS_INTERNOS,
                titulo="Cita reagendada",
                mensaje="",
                cita=update,
                asesor=asesor,
            )
            nueva_notificacion_correo.enviar()

            return HttpResponse(status=200)


class AppointmentsView(APIView):
    def post(self, request):
        r = request.POST

        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = None
        
        print("usernamee")
        print(username)

        servicios_peticion = r.getlist("servicio")
        datos_cita = get_data_api(r, username)

        print("datos_cita")
        print(datos_cita)
        for servicio in servicios_peticion:
            servicio_db = ListaItemsServicios.objects.get(id=servicio)
            print(servicio_db)
            if servicio_db.familia != 3:
                datos_cita["servicio"] = servicio_db.nombre
                print(datos_cita)
                post = api.post(url=CITA_CREAR, data=json.dumps(datos_cita), headers=HEADERS)
                print(post.text)
                if post.status_code == 200:
                    respuesta = json.loads(post.text)
                    no_cita = respuesta["details"]["no_cita"]
                    id_hd = respuesta["details"]["id_hd"]
                    datos_cita["NumCita"] = no_cita

        print(post.json()["codigo"])
        if post.json()["codigo"] == 200:
            print("CITA CREADA EN TABLERO")
            lista_servicios_nombres = []
            for id_servicio in servicios_peticion:
                servicio = ListaItemsServicios.objects.get(id=id_servicio).nombre
                ActividadesCitasServicios.objects.create(no_cita=no_cita, servicio=servicio, id_servicio=id_servicio)
                lista_servicios_nombres.append(servicio)

        if post.json()["codigo"] == 200:
            print("SERVICIOS CREADOS")
            respuesta = json.loads(post.text)
            separador = ", "
            nueva_cita = ActividadesCitas.objects.create(
                no_cita=no_cita,
                id_hd=id_hd,
                id_asesor=datos_cita["id_asesor"],
                fecha_cita=datos_cita["fecha"].replace("/", "-"),
                no_placas=datos_cita["no_placas"],
                cliente=datos_cita["cliente"],
                correo=datos_cita["correo"],
                modelo_vehiculo=datos_cita["modelo"],
                color_vehiculo=datos_cita["color"],
                tiempo=datos_cita["tiempo"],
                year_vehiculo=datos_cita["ano"],
                vin=datos_cita["vin"],
                telefono=datos_cita["telefono"],
                hora_cita=datos_cita["hora_cita"],
                status="0",
                whatsapp=datos_cita["whatsapp"],
                kilometraje=datos_cita["kilometraje"],
                id_estado=1,
                comentario=separador.join(lista_servicios_nombres),
            )
            print("CITA CREADA")

            try:
                asesor = VCitasUsuarios.objects.get(cveasesor=datos_cita["id_asesor"]).nombre
            except Exception:
                asesor = ""

            datos_cita["asesor"] = asesor
            servicios = ListaItemsServicios.objects.filter(id__in=servicios_peticion).values_list("nombre", flat=True)

            CITA_CREAR_DINISSAN = "http://201.150.44.27:8985"
            datos_cita_dinissan = get_data_api_dinissan(r, no_cita)
            print(datos_cita_dinissan)
            post_dinissan = api.post(url=CITA_CREAR_DINISSAN, data=json.dumps(datos_cita_dinissan), headers=HEADERS, auth=('S0022951509', 'Cpi@012@21User*'))
            print(post_dinissan.text)

            if datos_cita["whatsapp"]:
                asyncio.run(whatsapp_citas(0, datos_cita["telefono"], datos_cita))

            asyncio.run(
                correo_citas(
                    0,
                    datos_cita["correo"],
                    datos_cita=datos_cita,
                    asesor=asesor,
                )
            )

            # Correo al contact center para notificar la creación de la cita
            nueva_notificacion_correo = NotificacionCorreo(
                direccion_email=settings.CITAS_CORREOS_INTERNOS,
                titulo="Nueva cita creada",
                mensaje="",
                cita=nueva_cita,
                asesor=asesor,
                servicios=servicios,
            )
            nueva_notificacion_correo.enviar()

            return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(auth_views.LoginView):
    # Vista de Login

    template_name = "citas_dinissan/login.html"
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # Verifica una condición para redirigir
        if not settings.LOGIN_REQUIRED:
            return HttpResponseRedirect(reverse_lazy('client_new', kwargs={'vin': " "}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = settings.AGENCIA
        context["settings"] = settings

        return context

class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    # Vista de Logout
    pass