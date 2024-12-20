import asyncio
import json
from datetime import datetime

import requests as api
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

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


class ClienteNuevaCita(TemplateView):
    template_name = "citas_dinissan/cliente_nueva_cita.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = settings.AGENCIA
        context["settings"] = settings

        context["ciudades"] = AgenciaTablero.objects.all().values_list("ciudad", flat=True).distinct()

        context["motivos_ingreso"] = MotivoIngreso.objects.all()

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
            response_info_cliente = api.post(
                "https://aplicaciones.grupovardi.com.co/CitasWebServicio/controllerCW/infoVehiculoCliente",
                json={"placa": request.data["placa"], "cedula": request.data["cedula"]},
                headers={"token": token, "tenant": "4"},
            )
            print(response_info_cliente)

            response_token = api.post(
                "https://dm-us.informaticacloud.com/authz-service/oauth/token?grant_type=client_credentials",
                auth=HTTPBasicAuth("3hN97ItSfCTguHjruDOMKF", "316L2sIdL")
            )
            token = response_token.json()["access_token"]

            response_plate = api.post(
                "https://apigw-pod1.dm-us.informaticacloud.com/t/8dbkbsgxnq1hgifvkspnoc.com/MCOL_03_VINES_INTEGRACION_Process",
                headers={'Authorization': f'Bearer {token}'},
                data={"Placa":request.data["placa"]}
            )

            try:
                info_response_plate = response_plate.json()["EspecificacionVehiculo"]
                print(info_response_plate)

                response = {
                    "ano": info_response_plate["anioModelo"],
                    "vin": info_response_plate["vin"],
                    "color": info_response_plate["color"],
                }
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

            if response_info_cliente.json()["codigo"] == 200:
                info_cliente = response_info_cliente.json()
                info_cliente["ano"] = response["ano"]
                info_cliente["vin"] = response["vin"]
                info_cliente["color"] = response["color"]
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
    parser_classes = [MultiPartParser]
    def post(self, request: Request, *args, **kwargs):
        print(request.data)

        query_dict = dict(request.data)

        if 'precios' not in query_dict:
            query_dict['precios'] = ['']

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
        datos_cita = get_data_api(r)

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
            post = api.post(url=CITA_CREAR, data=json.dumps(datos_cita), headers=HEADERS)
            print(post.text)
            if post.status_code == 200:
                respuesta = json.loads(post.text)
                no_cita = respuesta["details"]["no_cita"]
                try:
                    no_cita_vardi = json.loads(response_dinissan.text)["numeroCita"]
                except:
                    no_cita_vardi = None
                id_hd = respuesta["details"]["id_hd"]
                datos_cita["NumCita"] = no_cita


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
                    observaciones=datos_cita["comentarios"]
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

        servicios_peticion = r.getlist("servicio")
        datos_cita = get_data_api(r)

        print("datos_cita")
        print(datos_cita)
        for servicio in servicios_peticion:
            servicio_db = ListaItemsServicios.objects.get(id=servicio)
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
