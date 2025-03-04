from django.db import models

from django.contrib.auth.models import User


class AgenciaTablero(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_agencia = models.CharField(max_length=25)
    nombre = models.CharField(max_length=300)
    ciudad = models.CharField(max_length=300)
    url_api_tablero = models.CharField(max_length=300)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = True
        verbose_name = "Agencia"
        verbose_name_plural = "Agencias"


class MotivoIngreso(models.Model):
    id = models.CharField(max_length=3, primary_key=True, unique=True)
    descripcion_motivo = models.CharField(max_length=50, blank=True, null=True)
    estado = models.BooleanField()
    categoria_paquete = models.CharField(max_length=20, blank=True, null=True)
    nit_aseguradora = models.CharField(max_length=100, blank=True, null=True)
    adjuntos = models.BooleanField()
    observacion = models.CharField(max_length=240, blank=True, null=True)
    tipo = models.CharField(max_length=30, blank=True, null=True)
    grupo = models.CharField(max_length=80, blank=True, null=True)
    sintoma = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "motivos_ingreso"

class MotivoIngresoMazda(models.Model):
    id = models.CharField(max_length=3, primary_key=True, unique=True)
    descripcion_motivo = models.CharField(max_length=50, blank=True, null=True)
    estado = models.BooleanField()
    categoria_paquete = models.CharField(max_length=20, blank=True, null=True)
    nit_aseguradora = models.CharField(max_length=100, blank=True, null=True)
    adjuntos = models.BooleanField()
    observacion = models.CharField(max_length=240, blank=True, null=True)
    tipo = models.CharField(max_length=30, blank=True, null=True)
    grupo = models.CharField(max_length=80, blank=True, null=True)
    sintoma = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "motivos_ingreso_mazda"

class FallaSintoma(models.Model):
    id = models.CharField(max_length=3, primary_key=True, unique=True)
    descripcion_motivo = models.CharField(max_length=50, null=True, blank=True)
    tipo = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.CharField(max_length=240, null=True, blank=False)
    descripcion_auxiliar = models.CharField(max_length=50, null=True, blank=True)
    estado = models.BooleanField()
    modelo_tasa = models.CharField(max_length=10, null=True, blank=False)

    class Meta:
        managed = False
        db_table = "falla_sintoma"


class VCitasUsuarios(models.Model):
    cvegrupo = models.IntegerField(db_column="cveGrupo")
    cveperfil = models.IntegerField(db_column="cvePerfil")
    cveusuario = models.CharField(db_column="cveUsuario", max_length=15)
    pass_field = models.CharField(db_column="Pass", max_length=100)
    nombre = models.CharField(db_column="Nombre", max_length=150, blank=True, null=True)
    correoe = models.CharField(db_column="correoE", max_length=100, blank=True, null=True)
    color = models.CharField(db_column="Color", max_length=50, blank=True, null=True)
    cveasesor = models.CharField(db_column="cveAsesor", max_length=20, blank=True, null=True)
    activo = models.BooleanField(db_column="Activo")
    id_agencia = models.IntegerField(db_column="id_agencia", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "v_usuarios"


# Código legacy
class ActividadesCitas(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_cita = models.BigIntegerField(null=True, blank=True)
    no_cita_vardi = models.BigIntegerField(null=True, blank=True)
    id_tecnico = models.CharField(max_length=50, null=True, blank=True)
    id_asesor = models.CharField(max_length=50, null=True, blank=True)

    fecha_cita = models.DateField()
    no_placas = models.CharField(max_length=50, null=True, blank=True)
    cliente = models.CharField(max_length=300, null=True, blank=True)
    correo = models.CharField(max_length=300, null=True, blank=True)
    modelo_vehiculo = models.CharField(max_length=100, null=True, blank=True)
    color_vehiculo = models.CharField(max_length=50, null=True, blank=True)
    tiempo = models.IntegerField(null=True, blank=True)
    hora_rampa = models.TimeField(null=True, blank=True)
    year_vehiculo = models.IntegerField(null=True, blank=True)
    vin = models.CharField(max_length=50, null=True, blank=True)
    servicio = models.CharField(max_length=300, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    hora_cita = models.TimeField(null=True, blank=True)

    fecha_hora_fin = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    status = models.CharField(max_length=50, null=True, blank=True)
    whatsapp = models.BooleanField(default=False, null=True, blank=True)

    kilometraje = models.BigIntegerField(null=True, blank=True)
    id_hd = models.BigIntegerField(null=True, blank=True)
    id_estado = models.BigIntegerField(null=True, blank=True)

    comentario = models.CharField(max_length=1000, null=True, blank=True)
    id_agencia = models.IntegerField(max_length=50, null=True, blank=True)

    observaciones = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        managed = True
        db_table = "actividades_citas"
        verbose_name = "cita"
        verbose_name_plural = "Citas"


class ActividadesCitasServicios(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_cita = models.BigIntegerField(blank=True, null=True)
    id_servicio = models.BigIntegerField(blank=True, null=True)
    servicio = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "actividades_citas_servicios"
        verbose_name = "servicio solicitado"
        verbose_name_plural = "Servicios solicitados"


class ListaItemsModelos(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    tipo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_modelos"
        verbose_name = "modelo de vehículo"
        verbose_name_plural = "Modelos de vehículos"


class ListaItemsYears(models.Model):
    id = models.BigAutoField(primary_key=True)
    year = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_years"
        verbose_name = "año de vehículo"
        verbose_name_plural = "Años de vehículos"


class ListaItemsFamiliasServicios(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=150, blank=True, null=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    orden = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_familias_servicios"
        verbose_name = "familia de servicios"
        verbose_name_plural = "Familias de servicios"


class ListaItemsServicios(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_servicio = models.BigIntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    familia = models.BigIntegerField(blank=True, null=True)
    orden = models.BigIntegerField(blank=True, null=True)
    costo = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_servicios"
        verbose_name = "servicio"
        verbose_name_plural = "Servicios"


class VCitasTecnicos(models.Model):
    id_empleado = models.CharField(
        db_column="ID_EMPLEADO", max_length=10, primary_key=True
    )  # Field name made lowercase.
    id_tipo_empleado = models.CharField(
        db_column="ID_TIPO_EMPLEADO", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    nombre_empleado = models.CharField(
        db_column="NOMBRE_EMPLEADO", max_length=60, blank=True, null=True
    )  # Field name made lowercase.
    nivel = models.CharField(db_column="NIVEL", max_length=1, blank=True, null=True)  # Field name made lowercase.
    bahia = models.IntegerField(db_column="BAHIA", blank=True, null=True)  # Field name made lowercase.
    express = models.BooleanField(db_column="EXPRESS", blank=True, null=True)  # Field name made lowercase.
    color_tecnico = models.CharField(
        db_column="COLOR_TECNICO", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    hora_ent_lv = models.CharField(
        db_column="HORA_ENT_LV", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_sal_lv = models.CharField(
        db_column="HORA_SAL_LV", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_comer = models.CharField(
        db_column="HORA_COMER", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_ent_s = models.CharField(
        db_column="HORA_ENT_S", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_sal_s = models.CharField(
        db_column="HORA_SAL_S", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    id_asesor = models.CharField(
        db_column="ID_ASESOR", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    nombre_asesor = models.CharField(
        db_column="NOMBRE_ASESOR", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    no_emp_asesor = models.IntegerField(db_column="NO_EMP_ASESOR", blank=True, null=True)  # Field name made lowercase.
    jefe_taller = models.BooleanField(db_column="JEFE_TALLER", blank=True, null=True)  # Field name made lowercase.
    hora_ent_d = models.CharField(
        db_column="HORA_ENT_D", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_sal_d = models.CharField(
        db_column="HORA_SAL_D", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_comer_s = models.CharField(
        db_column="HORA_COMER_S", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_comer_d = models.CharField(
        db_column="HORA_COMER_D", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    id_empleado_bi = models.CharField(
        db_column="ID_EMPLEADO_BI", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    min_comer_lv = models.IntegerField(db_column="MIN_COMER_LV", blank=True, null=True)  # Field name made lowercase.
    min_comer_s = models.IntegerField(db_column="MIN_COMER_S", blank=True, null=True)  # Field name made lowercase.
    min_comer_d = models.IntegerField(db_column="MIN_COMER_D", blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "tecnicos"


class CitasStatusCita(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_cita = models.BigIntegerField(blank=True, null=True)
    fecha_hora_fin_cita = models.DateTimeField(blank=True, null=True)
    fecha_hora_confirmacion_cita = models.DateTimeField(blank=True, null=True)
    fecha_hora_fin_preinventario = models.DateTimeField(blank=True, null=True)
    fecha_hora_fin_prediagnostico = models.DateTimeField(blank=True, null=True)
    fecha_hora_fin_cancelacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "status_cita"


class VCitasTracker(models.Model):
    no_orden = models.CharField(max_length=25, blank=True, null=False, primary_key=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    tecnico = models.CharField(max_length=60, blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    hora_llegada = models.DateTimeField(blank=True, null=True)
    hora_inicio_asesor = models.DateTimeField(blank=True, null=True)
    hora_fin_asesor = models.DateTimeField(blank=True, null=True)
    hora_promesa = models.DateTimeField(blank=True, null=True)
    hora_grabado = models.CharField(max_length=5, blank=True, null=True)
    inicio_tecnico = models.DateTimeField(blank=True, null=True)
    fin_tecnico = models.DateTimeField(blank=True, null=True)
    detenido = models.CharField(max_length=5)
    servicio_capturado = models.CharField(max_length=500, blank=True, null=True)
    inicio_tecnico_lavado = models.DateTimeField(blank=True, null=True)
    fin_tecnico_lavado = models.DateTimeField(blank=True, null=True)
    ultima_actualizacion = models.IntegerField(blank=True, null=True)
    motivo_paro = models.CharField(max_length=22, blank=True, null=True)
    id_hd = models.CharField(max_length=25, blank=False, null=False)
    telefono_agencia = models.CharField(max_length=25, blank=False, null=False)

    class Meta:
        managed = False
        db_table = "v_tracker"


class VInformacionCitas(models.Model):
    id_hd = models.AutoField(primary_key=True)
    no_cita = models.CharField(max_length=25)
    no_orden = models.CharField(max_length=25)
    cliente = models.CharField(max_length=200, blank=True, null=True)
    hora_llegada = models.DateTimeField(blank=True, null=True)
    hora_retiro = models.DateTimeField(blank=True, null=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_informacion_citas"


class Log(models.Model):
    # Modelo de Log

    id_sesion = models.IntegerField(null=True)
    ip_address = models.CharField(max_length=100, null=True)
    placa = models.CharField(max_length=100, null=True)
    cedula = models.CharField(max_length=100, null=True)
    nombre = models.CharField(max_length=100, null=True)
    primer_apellido = models.CharField(max_length=100, null=True)
    segundo_apellido = models.CharField(max_length=100, null=True)
    celular = models.CharField(max_length=100, null=True)
    telefono_fijo = models.CharField(max_length=100, null=True)
    correo = models.CharField(max_length=100, null=True)
    direccion = models.CharField(max_length=100, null=True)
    tipo_de_relacion = models.CharField(max_length=100, null=True)
    medio_de_confirmacion = models.CharField(max_length=100, null=True)
    ultimo_km = models.CharField(max_length=100, null=True)
    km_actual = models.CharField(max_length=100, null=True)
    vin = models.CharField(max_length=100, null=True)
    descripcion_modelo_tasa = models.CharField(max_length=200, null=True)
    color = models.CharField(max_length=100, null=True)
    fecha_de_vencimiento_soat = models.CharField(max_length=100, null=True)
    fecha_de_vencimiento_tecnomecanica = models.CharField(max_length=100, null=True)
    motivo_de_ingreso = models.CharField(max_length=200, null=True)
    tipo_de_revision_o_paquete = models.CharField(max_length=200, null=True)
    comentarios = models.CharField(max_length=2000, null=True)
    ciudad = models.CharField(max_length=2000, null=True)
    punto_de_servicio = models.CharField(max_length=2000, null=True)
    fecha_cita = models.DateField(null=True)
    hora_cita = models.TimeField(null=True)
    fecha = models.DateField()
    hora = models.TimeField()

    no_cita = models.CharField(max_length=100, null=True)
    no_cita_vardi = models.CharField(max_length=100, null=True)
    id_hd = models.CharField(max_length=100, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        # Retorna el id
        return f"{self.id}"
    class Meta:
        verbose_name_plural = "Logs"

class DatosSalesForce(models.Model):
    vin = models.CharField(max_length=17, null=True, blank=True)
    placa = models.CharField(max_length=100, null=True, blank=True)
    motor = models.CharField(max_length=100, null=True, blank=True)
    codigoLinea = models.CharField(max_length=100, null=True, blank=True)
    descripcionLinea = models.CharField(max_length=100, null=True, blank=True)
    opcion = models.CharField(max_length=100, null=True, blank=True)
    vis = models.CharField(max_length=100, null=True, blank=True)
    codColor = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    version = models.CharField(max_length=100, null=True, blank=True)
    identificadorProducto = models.CharField(max_length=100, null=True, blank=True)
    anioModelo = models.CharField(max_length=100, null=True, blank=True)
    servicio = models.CharField(max_length=100, null=True, blank=True)
    fechaEntrega = models.CharField(max_length=100, null=True, blank=True)
    fechaMatricula = models.CharField(max_length=100, null=True, blank=True)
    ciudadPlaca = models.CharField(max_length=100, null=True, blank=True)
    codConcesionarioVendedor = models.CharField(max_length=100, null=True, blank=True)
    ConcesionarioVendedor = models.CharField(max_length=100, null=True, blank=True)
    campaniaSeguridadPendiente = models.IntegerField(null=True, blank=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Retorna el id
        return f"{self.id}"

    class Meta:
        verbose_name_plural = "DatosSalesForce"

class ScheduledTask(models.Model):

    appointment = models.ForeignKey(ActividadesCitas, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('executing', 'Executing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    )

    function_name = models.CharField(max_length=255)
    parameters = models.JSONField()
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.function_name} scheduled for {self.scheduled_date}"
