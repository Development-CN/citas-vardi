from datetime import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from citas_dinissan.models import ActividadesCitas, ActividadesCitasServicios
from citas_dinissan.models import CitasStatusCita as StatusCita
from citas_dinissan.models import ListaItemsServicios

from .coreapi import CoreAPI
from .models import *
from .utils import guardar_base_64, save_filepond, tracker_login

# from seguimientolite_hyundai_mx.models import Items


COREAPI_VIEWS = settings.COREAPI_INFORMACION

# LOGIN
class TrackerProLogin(TemplateView):
    template_name = "tracker_pro_toyota_mx/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = settings.AGENCIA
        context["settings"] = settings
        return context

    def post(self, request):
        no_placas = request.POST["placas"]

        context = {}
        context["agencia_nombre"] = settings.AGENCIA
        context["error"] = "Ingrese un numero de placa valido"
        # HACER LOGIN DE CLIENTE
        if no_placas:
            if tracker_login(request, no_placas):
                return redirect("tracker_pro")
            else:
                return render(request, "tracker_pro_toyota_mx/login.html", context)
        else:
            return render(request, "tracker_pro_toyota_mx/login.html", context)


# PANTALLA PRINCIPAL
class TrackerProView(LoginRequiredMixin, TemplateView):
    login_url = "tracker_pro_login"
    template_name = "tracker_pro_toyota_mx/cliente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.request.user
        no_cita = cliente.username

        # STATUS CITAS
        if isinstance(no_cita, str):
            try:
                StatusCita.objects.get(no_cita=no_cita)
            except Exception:
                fecha_hora_fin_cita = ActividadesCitas.objects.get(no_cita=no_cita).fecha_hora_fin
                StatusCita.objects.create(no_cita=no_cita, fecha_hora_fin_cita=fecha_hora_fin_cita)

            context["log"] = StatusCita.objects.get(no_cita=no_cita)
            context["agencia_nombre"] = settings.AGENCIA
            context["agencia_nombre_maps"] = str(settings.AGENCIA).replace(" ", "+")
            context["agencia_correo"] = settings.EMAIL_HOST_USER
            context["agencia_telefono"] = settings.TELEFONO
            context["cliente"] = cliente

            context["cita"] = ActividadesCitas.objects.filter(no_cita=no_cita).first()
            context["preinventario"] = ActividadesPreinventario.objects.filter(no_cita=no_cita)
            context["familias_prediagnostico"] = ListaItemsFamiliasPrediagnostico.objects.all()
            context["prediagnostico"] = ActividadesPrediagnostico.objects.filter(no_cita=no_cita, existencia=True)

            # TRACKER CLASICO
            try:
                if COREAPI_VIEWS:
                    core_api = CoreAPI("citas")
                    context["fecha_hora_llegada"] = core_api.post(no_cita=no_cita).query_object
                else:
                    context["fecha_hora_llegada"] = VInformacionCitas.objects.get(no_cita=no_cita)
                context["tracker"] = tracker_clasico(context["fecha_hora_llegada"].no_orden)
                context["documentos_digitales"] = {}  # settings.TRACKER_PRO_DOCUMENTOS

                for boton, url in settings.TRACKER_PRO_DOCUMENTOS.items():
                    context["documentos_digitales"][boton] = str(url).replace(
                        "{{id_hd}}", str(context["tracker"]["details"].id_hd)
                    )
            except Exception as e:
                print(e)

            # SEGUIMIENTO EN LINEA
            try:
                if COREAPI_VIEWS:
                    core_api = CoreAPI("citas")
                    no_orden = core_api.post(no_cita=no_cita).query_object.no_orden
                else:
                    no_orden = VInformacionCitas.objects.get(no_cita=no_cita).no_orden
                hoja_multipuntos = Items.objects.filter(no_orden=no_orden)
                if hoja_multipuntos:
                    context["hoja_multipuntos"] = True
            except Exception as e:
                print(e)

        return context

    def post(self, request):
        cliente = self.request.user
        no_cita = cliente.username

        if request.POST.get("confirmar_cita", None):
            update = StatusCita.objects.get(no_cita=no_cita)
            update.fecha_hora_confirmacion_cita = datetime.now()
            update.save()

            try:
                update_cita = ActividadesCitas.objects.get(no_cita=no_cita)
                update_cita.id_estado = 2
                update_cita.save()
            except Exception as error:
                print(error)
            return HttpResponse(status=200)


# PRE-INVENTARIO
class PreInventarioView(LoginRequiredMixin, TemplateView):
    login_url = "tracker_pro_login"
    template_name = "tracker_pro_toyota_mx/preinventario.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = "Capital Network"
        context["items_familias_preinventario"] = ListaItemsFamiliasPreinventario.objects.all()
        context["items_preinventario"] = ListaItemsPreinventario.objects.all()
        return context

    def post(self, request):
        r = request.POST
        print(r)
        cliente = self.request.user
        if r.get("guardado_preinventario", None):
            try:
                print("GUARDADO DE PREINVENTARIO")
                evidencia = r.get("evidencia", None)
                save_filepond(r.get("fp_id", None))

                existencia = r.get("existencia", None)
                if existencia == "true":
                    existencia = True
                else:
                    existencia = False

                comentarios = r.get("comentarios", None)
                if comentarios == "undefined":
                    comentarios = ""

                ActividadesPreinventario.objects.create(
                    no_cita=cliente.username,
                    nombre=r["nombre"],
                    familia=r["familia"],
                    comentarios=comentarios,
                    existencia=existencia,
                    evidencia=evidencia,
                )

                # LOG
                try:
                    update = StatusCita.objects.get(no_cita=cliente.username)
                    update.fecha_hora_fin_preinventario = datetime()
                    update.save()
                except Exception:
                    pass
                return HttpResponse(status=200)
            except Exception as e:
                print(e)
                return HttpResponse(status=400)

        if r.get("guardado_firma", None):
            guardar_base_64(r["firma"], cliente.username, "preinventario")
            print("FIRMA GUARDADA")
            return HttpResponse(status=200)


# PRE-DIAGNOSTICO
class PreDiagnosticoView(LoginRequiredMixin, TemplateView):
    login_url = "tracker_pro_login"
    template_name = "tracker_pro_toyota_mx/prediagnostico.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agencia_nombre"] = "Capital Network"
        context["items_familias_preinventario"] = ListaItemsFamiliasPrediagnostico.objects.all()
        context["items_preinventario"] = ListaItemsPrediagnostico.objects.all()
        return context

    def post(self, request):
        r = request.POST
        cliente = self.request.user
        if r.get("guardado_preinventario", None):
            try:
                print("GUARDADO DE PREINVENTARIO")
                evidencia = r.get("evidencia", None)
                save_filepond(r.get("fp_id", None))

                existencia = r.get("existencia", None)
                if existencia == "true":
                    existencia = True
                else:
                    existencia = False

                comentarios = r.get("comentarios", None)
                if comentarios == "undefined":
                    comentarios = ""

                ActividadesPrediagnostico.objects.create(
                    no_cita=cliente.username,
                    nombre=r["nombre"],
                    familia=r["familia"],
                    comentarios=comentarios,
                    existencia=existencia,
                    evidencia=evidencia,
                )

                # LOG
                try:
                    update = StatusCita.objects.get(no_cita=cliente.username)
                    update.fecha_hora_fin_prediagnostico = datetime()
                    update.save()
                except Exception:
                    pass
                return HttpResponse(status=200)
            except Exception:
                return HttpResponse(status=200)

        if r.get("guardado_firma", None):
            guardar_base_64(r["firma"], cliente.username, "prediagnostico")
            print("FIRMA GUARDADA")
            return HttpResponse(status=200)


# LOGOUT
class TrackerProLogout(LogoutView):
    next_page = "tracker_pro_login"


# TRACKER CLASICO
def tracker_clasico(no_orden):
    if COREAPI_VIEWS:
        core_api = CoreAPI("tracker_detalle")
        query = core_api.get().queryset
    else:
        query = VTracker.objects.filter(no_orden=no_orden)

    chips = len(query)
    operaciones = None

    if chips == 1:
        details = query[0]
    elif chips > 1:
        details = query[0]
        operaciones = query[1:chips]

    e_recepcion = "completed"
    e_asesor = "inactive"
    e_tecnico = "inactive"
    e_lavado = "inactive"
    e_entrega = "inactive"

    estados = [
        details.hora_inicio_asesor,
        details.hora_fin_asesor,
        details.inicio_tecnico,
        details.fin_tecnico,
        details.inicio_tecnico_lavado,
        details.fin_tecnico_lavado,
    ]

    mensajes = [
        "Su vehículo se encuentra en manos de un asesor.",
        "En breve su vehículo ingresará al taller de servicio.",
        "Su vehículo se encuentra en manos de un experto técnico",
        "Su vehículo ha salido del taller de servicio,  ingresara al area de lavado en breve.",
        "En unos momentos mas su vehículo estará listo para ser entregado.",
        "Su vehículo esta listo",
        "Su vehículo se encuentra detenido",
        "Su vehículo se encuentra detenido debido a que se necesita su autorización para continuar el proceso.",
        "En breve su asesor se comunicara con usted",
        "(Mensaje de pruebaruta)",
        "(Mensaje de cal+idad)",
        "(Mensaje de tot)",
    ]

    inactivos = [i for i, x in enumerate(estados) if not x]

    if details.ultima_actualizacion < 60:
        min = details.ultima_actualizacion
        if min == 1:
            u_actualizacion = f"{min:.0f} Minuto"
        else:
            u_actualizacion = f"{min:.0f} Minutos"
    elif details.ultima_actualizacion > 60 and details.ultima_actualizacion < 1440:
        min = details.ultima_actualizacion / 60
        if min < 2:
            u_actualizacion = f"{min:.0f} Hora"
        else:
            u_actualizacion = f"{min:.0f} Horas"
    elif details.ultima_actualizacion > 1440:
        min = details.ultima_actualizacion / 1440
        if min < 2:
            u_actualizacion = f"{min:.0f} Dia"
        else:
            u_actualizacion = f"{min:.0f} Dias"

    if inactivos == []:
        e_recepcion = "completed"
        e_asesor = "completed"
        e_tecnico = "completed"
        e_lavado = "completed"
        if details.motivo_paro is None:
            e_entrega = "active"
            serv_actual = "Status Actual: Listo Para Entrega"
            m_actual = mensajes[5]
        elif details.motivo_paro == "Autorización":
            e_entrega = "inactive"
            serv_actual = "Status actual: Detenido Por Autorización"
            m_actual = mensajes[7]
        else:
            e_entrega = "inactive"
            serv_actual = "Status actual: Detenido"
            m_actual = mensajes[6]

    elif inactivos[0] == 1:
        if details.motivo_paro is None:
            e_asesor = "active"
            serv_actual = "Status Actual: Asesor"
            m_actual = mensajes[0]
        elif details.motivo_paro == "Autorización":
            e_asesor = "inactive"
            serv_actual = "Status Actual: Detenido Por Autorización"
            m_actual = mensajes[7]
        else:
            e_asesor = "inactive"
            serv_actual = "Status Actual: Detenido"
            m_actual = mensajes[6]

    elif inactivos[0] == 2:
        if details.motivo_paro is None:
            e_asesor = "completed"
            serv_actual = "Ultimo Status: Asesor"
            m_actual = mensajes[1]
        elif details.motivo_paro == "Autorización":
            e_asesor = "inactive"
            serv_actual = "Status Actual: Detenido Por Autorización"
            m_actual = mensajes[7]
        else:
            e_asesor = "inactive"
            serv_actual = "Ultimo Status: Detenido"
            m_actual = mensajes[6]

    elif inactivos[0] == 3:
        e_asesor = "completed"
        if details.motivo_paro is None:
            e_tecnico = "active"
            serv_actual = "Status Actual: Servicio"
            m_actual = mensajes[2]
        elif details.motivo_paro == "Autorización":
            e_tecnico = "inactive"
            serv_actual = "Status Actual: Detenido Por Autorización"
            m_actual = mensajes[7]
        else:
            e_tecnico = "inactive"
            serv_actual = "Status Actual: Detenido"
            m_actual = mensajes[6]

    elif inactivos[0] == 4:
        e_asesor = "completed"
        if details.motivo_paro is None:
            e_tecnico = "completed"
            serv_actual = "Ultimo Status: Servicio"
            m_actual = mensajes[3]
        elif details.motivo_paro == "Autorización":
            e_tecnico = "inactive"
            serv_actual = "Status Actual: Detenido Por Autorización"
            m_actual = mensajes[7]
        else:
            e_tecnico = "inactive"
            serv_actual = "Ultimo Status: Detenido"
            m_actual = mensajes[6]

    elif inactivos[0] == 5:
        e_asesor = "completed"
        e_tecnico = "completed"
        if details.motivo_paro is None:
            e_lavado = "active"
            serv_actual = "Status Actual: Lavado"
            m_actual = mensajes[4]
        elif details.motivo_paro == "Autorización":
            e_lavado = "inactive"
            serv_actual = "Status Actual: Detenido Por Autorización"
            m_actual = mensajes[7]
        else:
            e_lavado = "inactive"
            serv_actual = "Status Actual: Detenido"
            m_actual = mensajes[6]

    context_tracker = {
        "chips": chips,
        "details": details,
        "e_recepcion": e_recepcion,
        "e_asesor": e_asesor,
        "e_tecnico": e_tecnico,
        "e_lavado": e_lavado,
        "e_entrega": e_entrega,
        "serv_actual": serv_actual,
        "m_actual": m_actual,
        "u_actualizacion": u_actualizacion,
        "range": range(1, (chips)),
        "operaciones": operaciones,
    }

    return context_tracker


# API DE CONSULTA
class TrackerProAPI(APIView):
    # CONSULTA DE INFORMACION
    def post(self, request):
        r = request.data
        if r.get("no_cita", None):
            no_cita = r.get("no_cita", None)
            cita = ActividadesCitas.objects.get(no_cita=no_cita)
            status_general = StatusCita.objects.filter(no_cita=no_cita).first()

            query_diagnostico = ActividadesPrediagnostico.objects.filter(no_cita=no_cita).values(
                "nombre", "comentarios", "evidencia", "existencia"
            )
            query_inventario = ActividadesPreinventario.objects.filter(no_cita=no_cita).values(
                "nombre", "comentarios", "evidencia", "existencia"
            )

            servicios = ActividadesCitasServicios.objects.filter(no_cita=no_cita).values_list("id_servicio")
            query_servicios = ListaItemsServicios.objects.filter(id__in=servicios).values(
                "nombre", "descripcion", "costo"
            )

            if status_general:
                if status_general.fecha_hora_fin_cita and not status_general.fecha_hora_confirmacion_cita:
                    status_cita = "NO CONFIRMADA"
                if status_general.fecha_hora_confirmacion_cita:
                    status_cita = "CONFIRMADA"
                if status_general.fecha_hora_fin_cancelacion:
                    status_cita = "CANCELADA"
            else:
                status_cita = "SIN ESTATUS"

            response = {}
            response["no_cita"] = no_cita
            response["id_estado"] = cita.id_estado
            response["cliente"] = cita.cliente
            response["kilometraje"] = cita.kilometraje
            response["telefono"] = cita.telefono
            response["email"] = cita.correo
            response["fecha_cita"] = cita.fecha_cita
            response["hora_cita"] = cita.hora_cita
            response["status"] = status_cita
            response["preinventario"] = query_inventario
            response["prediagnostico"] = query_diagnostico
            response["servicios"] = query_servicios

            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"error": "no se encontro el numero de cita"},
                status=status.HTTP_404_NOT_FOUND,
            )


class TrackerProEstados(APIView):
    def post(self, request):
        r = request.data
        lista_vin = r.get("lista_vin", None)
        if isinstance(lista_vin, (list, tuple)):
            informacion_citas = ActividadesCitas.objects.filter(vin__in=lista_vin).values()
            if informacion_citas:
                return Response(data=informacion_citas, status=status.HTTP_200_OK)
            else:
                return Response(data={"error": "no results"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data={"error": "invalid data type"}, status=status.HTTP_400_BAD_REQUEST)
