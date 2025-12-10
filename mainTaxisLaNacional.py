import sqlite3
from sqlite3 import Error
import re #Validacion correo
from datetime import datetime # Fechas y horas
import os #Verificar ruta de BD
#----QtableWidget----#
from PyQt5.QtWidgets import QTableWidgetItem, QVBoxLayout, QHeaderView, QTableWidget
# para ajustar tabla a ventana # Ajustar columnas
from QTable import * #Archivo de QTableWidget convertido a .py necesario
import sys
# --- IMPORTS PARA GENERAR PDF ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter # Define el tamaño y tipo de pagina
from reportlab.lib.styles import getSampleStyleSheet #Estilo de textos predefinidos
from reportlab.lib import colors #Colores predefinidos

# Verificar si reportlab está instalado
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Advertencia: reportlab no está instalado. La generación de PDFs no estará disponible.")
    print("Instálalo con: pip install reportlab")


DB_FILENAME = "BDTaxisLaNacional.db"
# ---------------------------
# Helper: manejo de fechas
# ---------------------------
def pedir_fecha(mensaje, allow_empty=False):
    """
    Pide fecha en formato DD/MM/YYYY.
    Retorna string en formato YYYY-MM-DD para guardar en BD, o None si vacío y allow_empty True.
    """
    while True:
        fecha_str = input(mensaje).strip()
        if allow_empty and fecha_str == "":
            return None
        try:
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            return fecha_obj.strftime("%Y-%m-%d")
        except ValueError:
            print("Formato inválido. Use DD/MM/YYYY. Intente de nuevo.")

def pedir_fecha_vacia(mensaje):
    return pedir_fecha(mensaje, allow_empty=True)

# ---------------------------
# Clase para conexión DB
# ---------------------------
class Database:
    def __init__(self, filename=DB_FILENAME):
        self._filename = filename
        self._con = None

    def conectar(self):
        try:
            self._con = sqlite3.connect(self._filename)
            # enable foreign keys if needed in future
            self._con.execute("PRAGMA foreign_keys = ON;")
            return self._con
        except Error as e:
            print("Error al conectar DB:", e)
            return None

    def cerrar(self):
        if self._con:
            self._con.close()
            self._con = None

    @property
    def conexion(self):
        if self._con is None:
            return self.conectar()
        return self._con

# ---------------------------
# CLASE PADRE: BaseEntidad
# ---------------------------
class BaseEntidad:
    tabla = None          # debe ser sobrescrito
    pk = None             # nombre del campo PK
    campos = []           # lista de campos en orden para INSERT

    def __init__(self, db: Database, **kwargs):
        self._db = db
        # carga atributos dinámicamente desde kwargs
        for k, v in kwargs.items():
            setattr(self, f"_{k}", v)

    # --------- Operaciones DB genéricas ----------
    @classmethod
    def crear_tabla(cls, con):
        """Sobrescribir en subclases o usar SQL general si es posible."""
        raise NotImplementedError

    def guardar(self):
        """Inserta la entidad en la BD usando self.campos"""
        con = self._db.conexion
        cursor = con.cursor()
        valores = []
        for c in self.campos:
            valores.append(getattr(self, f"_{c}", None))
        placeholders = ",".join(["?"] * len(self.campos))
        sql = f"INSERT INTO {self.tabla} ({','.join(self.campos)}) VALUES ({placeholders})"
        cursor.execute(sql, valores)
        con.commit()
        return cursor.lastrowid

    @classmethod
    def consultar_por_pk(cls, con, valor_pk):
        cursor = con.cursor()
        sql = f"SELECT * FROM {cls.tabla} WHERE {cls.pk} = ?"
        cursor.execute(sql, (valor_pk,))
        return cursor.fetchone()

    @classmethod
    def listar_todos(cls, con):
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM {cls.tabla}")
        return cursor.fetchall()

    def mostrar_info(self):
        """Método polimórfico - ser sobrescrito por subclases"""
        print(f"<{self.__class__.__name__}> (entidad base)")

# ---------------------------
# CLASE Vehiculo
# ---------------------------
class Vehiculo(BaseEntidad):
    tabla = "infoVehiculos"
    pk = "placa"
    campos = [
        "placa","marca","referencia","modelo","numeroChasis","numeroMotor",
        "color","concesionario","fechaCompraVehiculo","tiempoGarantia",
        "fechaCompraPoliza","proveedorPoliza","fechaCompraSegObliga",
        "proveedorSegObliga","activo"
    ]

    @classmethod
    def crear_tabla(cls, con):
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS infoVehiculos(
                                placa text NOT NULL,
                                marca text NOT NULL, 
                                referencia text NOT NULL,
                                modelo integer NOT NULL,
                                numeroChasis text NOT NULL,
                                numeroMotor text NOT NULL,
                                color text NOT NULL,
                                concesionario text NOT NULL,
                                fechaCompraVehiculo date NOT NULL, 
                                tiempoGarantia integer NOT NULL,
                                fechaCompraPoliza date NOT NULL,
                                proveedorPoliza text NOT NULL,
                                fechaCompraSegObliga date NOT NULL,
                                proveedorSegObliga text NOT NULL,
                                activo integer NOT NULL,
                                PRIMARY KEY(placa))''')
        con.commit()

    # Encapsulamiento con property (ejemplo solicitado)
    @property
    def color(self):
        return getattr(self, "_color", None)

    @color.setter
    def color(self, nuevo_color):
        self._color = nuevo_color

    @property
    def activo(self):
        return getattr(self, "_activo", None)

    @activo.setter
    def activo(self, nuevo):
        if str(nuevo) not in ("1","2"):
            raise ValueError("Activo debe ser '1' o '2'")
        self._activo = int(nuevo)

    def mostrar_info(self):
        print("--------------- FICHA VEHÍCULO ---------------")
        for c in self.campos:
            val = getattr(self, f"_{c}", None)
            print(f"{c}: {val}")
        print("---------------------------------------------")

    # métodos de utilidad
    @classmethod
    def validar_placa(cls, con, placa):
        """Retorna fila si existe, sino None"""
        return cls.consultar_por_pk(con, placa)

    @classmethod
    def actualizar_poliza(cls, con, placa, nueva_fecha_poliza):
        cursor = con.cursor()
        # validar formato: asumimos que se recibe YYYY-MM-DD
        try:
            nueva = datetime.strptime(nueva_fecha_poliza, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Formato de fecha inválido (esperado YYYY-MM-DD)")
        fila = cls.consultar_por_pk(con, placa)
        if not fila:
            raise LookupError("Placa no encontrada")
        fecha_anterior = datetime.strptime(fila[10], "%Y-%m-%d").date()
        if nueva <= fecha_anterior:
            raise ValueError("La nueva fecha debe ser mayor que la anterior")
        cursor.execute("UPDATE infoVehiculos SET fechaCompraPoliza = ? WHERE placa = ?", (nueva_fecha_poliza, placa))
        con.commit()

    @classmethod
    def actualizar_indicador(cls, con, placa, nuevo_estado):
        if str(nuevo_estado) not in ("1","2"):
            raise ValueError("Estado inválido")
        cursor = con.cursor()
        cursor.execute("UPDATE infoVehiculos SET activo = ? WHERE placa = ?", (int(nuevo_estado), placa))
        con.commit()

# ---------------------------
# CLASE Conductor
# ---------------------------
class Conductor(BaseEntidad):
    tabla = "infoConductor"
    pk = "identificacion"
    campos = [
        "identificacion","nombre","apellido","direccion","telefono","correo",
        "placaVehiculo","fechaIngreso","fechaRetiro","indicadorContratado",
        "turno","valorTurno","valorAhorro","valorAdeuda","totalAhorrado"
    ]

    @classmethod
    def crear_tabla(cls, con):
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS infoConductor(
                                identificacion integer NOT NULL,
                                nombre text NOT NULL, 
                                apellido text NOT NULL,
                                direccion text NOT NULL,
                                telefono integer NOT NULL,
                                correo text NOT NULL,
                                placaVehiculo text NOT NULL,
                                fechaIngreso date NULL,
                                fechaRetiro date NULL,
                                indicadorContratado integer NOT NULL,
                                turno integer NOT NULL,
                                valorTurno integer NOT NULL,
                                valorAhorro integer NOT NULL,
                                valorAdeuda integer NOT NULL,
                                totalAhorrado integer NOT NULL,
                                PRIMARY KEY(identificacion))''')
        con.commit()
        ##------------------------------------------------------#
        #--------------ENCAPSULAMIENTO, PROPI. CON VALIDACION---#
    @property
    def correo(self):
        """Getter para el correo"""
        return getattr(self, "_correo", None)

    @correo.setter
    def correo(self, nuevo_correo):
        """Setter con validación"""
        if not nuevo_correo:
            raise ValueError("El correo no puede estar vacío")
        
        # Validar el formato del correo
        valido, mensaje = validar_correo(nuevo_correo)
        if not valido:
            raise ValueError(f"Correo inválido: {mensaje}")
        
        self._correo = nuevo_correo

    @property
    def telefono(self):
        return getattr(self, "_telefono", None)

    @telefono.setter
    def telefono(self, nuevo_telefono):
        """Setter con validación para teléfono"""
        if not str(nuevo_telefono).isdigit():
            raise ValueError("El teléfono debe contener solo números")
        self._telefono = int(nuevo_telefono)

    def mostrar_info(self):
        print("------------ INFORMACIÓN CONDUCTOR -------------")
        for c in self.campos:
            val = getattr(self, f"_{c}", None)
            print(f"{c}: {val}")
        print("-----------------------------------------------")

    @classmethod
    def validar_conductor(cls, con, identificacion):
        return cls.consultar_por_pk(con, identificacion)

    @staticmethod
    def validar_contrato(fecIngreso, fecRetiro):
        """
        POLIMORFISMO: Este método implementa una lógica específica de negocio
        que varía según el estado del contrato.
        """
        while True:
            indicador = input("Indicador contrato: Contratado[1], No contratado[2], Despedido[3]: ").strip()
            if indicador not in ("1","2","3"):
                print("Seleccione 1, 2 o 3")
                continue
            indicador = int(indicador)
            if indicador == 1 and fecIngreso is not None and fecRetiro is None:
                print("Estado: Contratado")
                return indicador
            elif indicador == 2 and fecIngreso is None and fecRetiro is None:
                print("Estado: No contratado")
                return indicador
            elif indicador == 3 and fecIngreso is not None and fecRetiro is not None:
                print("Estado: Despedido")
                return indicador
            else:
                print("Las fechas no coinciden con el estado seleccionado. Intente de nuevo.")
                # se repite el loop


    def mostrar_info(self):
        print("------------ INFORMACIÓN CONDUCTOR -------------")
        for c in self.campos:
            val = getattr(self, f"_{c}", None)
            print(f"{c}: {val}")
        print("-----------------------------------------------")

    @classmethod
    def validar_conductor(cls, con, identificacion):
        return cls.consultar_por_pk(con, identificacion)

    @staticmethod
    def validar_contrato(fecIngreso, fecRetiro):
        """
        Lógica para validar indicador de contrato:
        Contratado[1] -> fecIngreso != None y fecRetiro == None
        No contratado[2] -> fecIngreso == None y fecRetiro == None
        Despedido[3] -> fecIngreso != None y fecRetiro != None
        """
        while True:
            indicador = input("Indicador contrato: Contratado[1], No contratado[2], Despedido[3]: ").strip()
            if indicador not in ("1","2","3"):
                print("Seleccione 1, 2 o 3")
                continue
            indicador = int(indicador)
            if indicador == 1 and fecIngreso is not None and fecRetiro is None:
                print("Estado: Contratado")
                return indicador
            elif indicador == 2 and fecIngreso is None and fecRetiro is None:
                print("Estado: No contratado")
                return indicador
            elif indicador == 3 and fecIngreso is not None and fecRetiro is not None:
                print("Estado: Despedido")
                return indicador
            else:
                print("Las fechas no coinciden con el estado seleccionado. Intente de nuevo.")
                # se repite el loop
# ---------------------------
# VALIDACIÓN DE CORREO ELECTRÓNICO
# ---------------------------
def validar_correo(correo):
    """Valida el formato de un correo electrónico usando regex"""
    if not correo or not correo.strip():
        return False, "El correo no puede estar vacío"
    
    # Patrón para correo electrónico
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(patron, correo.strip()):
        return False, "Formato de correo inválido. Ejemplo: usuario@dominio.com"
    
    return True, "Correo válido"

def solicitar_correo_validado(mensaje="Correo: ", valor_actual=None):
    
    while True:
        correo = input(mensaje).strip()
        
        # Si hay valor actual y el usuario deja vacío, mantener el actual
        if valor_actual is not None and correo == "":
            return valor_actual
        
        # Validar el correo
        valido, mensaje_error = validar_correo(correo)
        
        if valido:
            return correo
        else:
            print(f"Error: {mensaje_error}")
            print("Por favor, ingrese un correo válido.")
            print("Ejemplo: jorge.perez@gmail.com\n")

# ---------------------------
# CLASE Mantenimiento
# ---------------------------
class Mantenimiento(BaseEntidad):
    tabla = "mantenimientoVehiculo"
    pk = "numeroOrden"
    campos = ["numeroOrden","placaVehiculo","nit","nombreProveedor","descripcionServicio","valorFacturado","fechaServicio"]

    @classmethod
    def crear_tabla(cls, con):
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS mantenimientoVehiculo(
                                numeroOrden integer NOT NULL,
                                placaVehiculo text NOT NULL, 
                                nit text NOT NULL,
                                nombreProveedor text NOT NULL,
                                descripcionServicio text NOT NULL,
                                valorFacturado integer NOT NULL,
                                fechaServicio date NOT NULL,
                                PRIMARY KEY(numeroOrden))''')
        con.commit()

    def mostrar_info(self):
        print("---------- MANTENIMIENTO ----------")
        for c in self.campos:
            val = getattr(self, f"_{c}", None)
            print(f"{c}: {val}")
        print("----------------------------------")

    @classmethod
    def consultar_por_numero(cls, con, numeroOrden):
        return cls.consultar_por_pk(con, numeroOrden)

    @classmethod
    def borrar_por_numero(cls, con, numeroOrden):
        cur = con.cursor()
        cur.execute("DELETE FROM mantenimientoVehiculo WHERE numeroOrden = ?", (numeroOrden,))
        con.commit()

    @classmethod
    def max_fecha_por_placa(cls, con, placa):
        cur = con.cursor()
        cur.execute("SELECT MAX(fechaServicio) FROM mantenimientoVehiculo WHERE placaVehiculo=?", (placa,))
        return cur.fetchone()[0]

    @classmethod
    def suma_valores(cls, con):
        cur = con.cursor()
        cur.execute("SELECT SUM(valorFacturado) FROM mantenimientoVehiculo")
        return cur.fetchone()[0]

# ---------------------------
# FUNCIONES DE LECTURA (crear objetos desde input)
# ---------------------------
def leer_info_vehiculo_input():
    placa = input("Placa vehiculo: ").strip()
    marca = input("Marca: ").strip()
    referencia = input("Referencia: ").strip()
    modelo = int(input("Modelo: ").strip())
    numeroChasis = input("Numero Chasis: ").strip()
    numeroMotor = input("Numero de motor: ").strip()
    color = input("Color: ").strip()
    concesionario = input("Concesionario: ").strip()
    fechaCompra = pedir_fecha("Fecha de compra (DD/MM/YYYY): ")
    tiempoGarantia = int(input("Tiempo garantia (meses): ").strip())
    fechaCompraPoliza = pedir_fecha("Fecha compra poliza (DD/MM/YYYY): ")
    proveedorPoliza = input("Proveedor poliza: ").strip()
    fechaCompraSeguroOblig = pedir_fecha("Fecha de compra seguro obligatorio (DD/MM/YYYY): ")
    proveedorSeguroOblig = input("Proveedor de seguro: ").strip()
    activo = input("Estado: Activo[1] Inactivo[2]: ").strip()
    if activo not in ("1","2"):
        print("Estado inválido, se asigna 1 (Activo).")
        activo = "1"
    datos = {
        "placa": placa, "marca": marca, "referencia": referencia, "modelo": modelo,
        "numeroChasis": numeroChasis, "numeroMotor": numeroMotor, "color": color,
        "concesionario": concesionario, "fechaCompraVehiculo": fechaCompra,
        "tiempoGarantia": tiempoGarantia, "fechaCompraPoliza": fechaCompraPoliza,
        "proveedorPoliza": proveedorPoliza, "fechaCompraSegObliga": fechaCompraSeguroOblig,
        "proveedorSegObliga": proveedorSeguroOblig, "activo": int(activo)
    }
    return datos

def leer_info_conductor_input(con: sqlite3.Connection):
    identificacion = input("Identificacion Conductor: ").strip()
    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()
    direccion = input("Direccion: ").strip()
    telefono = input("Telefono: ").strip()
    while not telefono.isdigit():
        telefono = input("Debe ser numérico. Intente otra vez: ").strip()
    correo = solicitar_correo_validado("Correo: ")
    # validar placa
    #  existente
    placa = input("Placa vehiculo asignada: ").strip()
    if not Vehiculo.validar_placa(con, placa):
        print("Placa no registrada. Use una placa existente o registre el vehículo primero.")
    fechaIngreso = pedir_fecha_vacia("Fecha de ingreso (DD/MM/YYYY), deje vacío si no aplica: ")
    fechaRetiro = pedir_fecha_vacia("Fecha de retiro (DD/MM/YYYY), deje vacío si no aplica: ")
    # validar contrato
    indicador = Conductor.validar_contrato(fechaIngreso, fechaRetiro)
    turno = int(input("Turno (1=24h,2=12h): ").strip())
    valorTurno = float(input("Valor del turno: ").strip())
    valorAhorro = float(input("Valor Ahorro: ").strip())
    valorAdeuda = float(input("Valor a deuda: ").strip())
    totalAhorrado = float(input("Total Ahorrado: ").strip())

    datos = {
        "identificacion": identificacion, "nombre": nombre, "apellido": apellido,
        "direccion": direccion, "telefono": int(telefono), "correo": correo,
        "placaVehiculo": placa, "fechaIngreso": fechaIngreso, "fechaRetiro": fechaRetiro,
        "indicadorContratado": indicador, "turno": turno, "valorTurno": valorTurno,
        "valorAhorro": valorAhorro, "valorAdeuda": valorAdeuda, "totalAhorrado": totalAhorrado
    }
    return datos

def leer_info_mantenimiento_input(con: sqlite3.Connection):
    numeroOrden = int(input("Numero de Orden: ").strip())
    placaVehiculo = input("Placa: ").strip()
    if not Vehiculo.validar_placa(con, placaVehiculo):
        print("Placa no registrada. Registrar vehículo primero o use una placa válida.")
    nit = input("Nit Proveedor: ").strip()
    nombreProveedor = input("Nombre Proveedor: ").strip()
    descripcionServicio = input("Servicio Recibido: ").strip()
    valorFacturado = float(input("Valor Facturado: ").strip())
    fechaServicio = pedir_fecha("Fecha mantenimiento (DD/MM/YYYY): ")
    datos = {
        "numeroOrden": numeroOrden, "placaVehiculo": placaVehiculo, "nit": nit,
        "nombreProveedor": nombreProveedor, "descripcionServicio": descripcionServicio,
        "valorFacturado": valorFacturado, "fechaServicio": fechaServicio
    }
    return datos

#-------------------#
#----QTableWidget---#
#-------------------#
def qtable(con):
    from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView, QApplication, QMainWindow, QVBoxLayout, QWidget
    from PyQt5 import QtCore
    import sys

    # Consulta a la BD
    filas = Mantenimiento.listar_todos(con)

    # Definir columnas
    columnas = [
        "Número de Orden",
        "Placa",
        "NIT",
        "Proveedor",
        "Servicio",
        "Valor Facturado",
        "Fecha de Servicio"
    ]

    class VentanaTabla(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Consulta total de mantenimientos")
            self.resize(900, 600)

            # ---- Widget central ----
            contenedor = QWidget()
            layout = QVBoxLayout(contenedor)

            # ---- Tabla ----
            self.tabla = QTableWidget()
            self.tabla.setRowCount(len(filas))
            self.tabla.setColumnCount(len(columnas))
            self.tabla.setHorizontalHeaderLabels(columnas)

            # Evitar edición
            self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

            # Ajustar columnas al tamaño disponible
            self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # Habilitar ordenamiento
            self.tabla.setSortingEnabled(True)

            # Llenar tabla
            for row, fila in enumerate(filas):
                for col, valor in enumerate(fila):
                    item = QTableWidgetItem(str(valor))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.tabla.setItem(row, col, item)

            layout.addWidget(self.tabla)
            self.setCentralWidget(contenedor)

    app = QApplication(sys.argv)
    ventana = VentanaTabla()
    ventana.show()
    sys.exit(app.exec_())

# ---------------------------
# OPERACIONES DE ALTO NIVEL / MENÚ
# ---------------------------
def crear_tablas_todas(con):
    Vehiculo.crear_tabla(con)
    Conductor.crear_tabla(con)
    Mantenimiento.crear_tabla(con)
    print("Tablas creadas (si no existían).")

def menu_principal(db: Database):
    con = db.conexion
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Vehículos")
        print("2. Conductores")
        print("3. Mantenimientos")
        print("4. Ficha vehículo (PDF)")
        print("5. Crear tablas (si no existen)")
        print("0. Salir")
        opc = input("Opción: ").strip()
        if opc == "1":
            menu_vehiculos(con, db)
        elif opc == "2":
            menu_conductores(con, db)
        elif opc == "3":
            menu_mantenimientos(con, db)
        elif opc == "4":
            generar_ficha_vehiculo_pdf(con)
        elif opc == "5":
            crear_tablas_todas(con)
        elif opc == "0":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

# ---------- Menú Vehículos ----------
def menu_vehiculos(con, db):
    while True:
        print("\n--- VEHÍCULOS ---")
        print("1. Registrar vehículo")
        print("2. Consultar vehículo por placa")
        print("3. Actualizar póliza (fecha mayor a anterior)")
        print("4. Cambiar indicador activo")
        print("0. Volver")
        opc = input("Opción: ").strip()
        if opc == "1":
            datos = leer_info_vehiculo_input()
            v = Vehiculo(db, **datos)
            try:
                v.guardar()
                print("Vehículo guardado correctamente.")
            except Exception as e:
                print("Error guardando vehículo:", e)
        elif opc == "2":
            placa = input("Ingrese placa: ").strip()
            fila = Vehiculo.consultar_por_pk(con, placa)
            if not fila:
                print("Placa no encontrada.")
            else:
                # construir objeto temporal para mostrar
                campos = dict(zip(Vehiculo.campos, fila))
                v = Vehiculo(db, **campos)
                v.mostrar_info()
        elif opc == "3":
            placa = input("Ingrese placa: ").strip()
            if not Vehiculo.validar_placa(con, placa):
                print("Placa no registrada.")
                continue
            nueva = pedir_fecha("Ingrese nueva fecha de compra de la póliza (DD/MM/YYYY): ")
            # convertir a YYYY-MM-DD
            try:
                nueva_ymd = datetime.strptime(nueva, "%Y-%m-%d").strftime("%Y-%m-%d") if "-" in nueva else datetime.strptime(nueva, "%Y-%m-%d").strftime("%Y-%m-%d")
            except Exception:
                # la función pedir_fecha retorna YYYY-MM-DD ya, así que simplemente pasar nueva
                nueva_ymd = nueva
            try:
                Vehiculo.actualizar_poliza(con, placa, nueva_ymd)
                print("Póliza actualizada.")
            except Exception as e:
                print("Error al actualizar póliza:", e)
        elif opc == "4":
            placa = input("Ingrese placa: ").strip()
            if not Vehiculo.validar_placa(con, placa):
                print("Placa no registrada.")
                continue
            nuevo_estado = input("Nuevo estado: Activo[1] Inactivo[2]: ").strip()
            try:
                Vehiculo.actualizar_indicador(con, placa, nuevo_estado)
                print("Indicador actualizado.")
            except Exception as e:
                print("Error actualizando indicador:", e)
        elif opc == "0":
            break
        else:
            print("Opción inválida.")

# ---------- Menú Conductores ----------
def menu_conductores(con, db):
    while True:
        print("\n--- CONDUCTORES ---")
        print("1. Registrar conductor")
        print("2. Consultar conductor por identificación")
        print("3. Actualizar (direccion/telefono/correo/fechas/adeuda/ahorrado)")
        print("0. Volver")
        opc = input("Opción: ").strip()
        if opc == "1":
            datos = leer_info_conductor_input(con)
            c = Conductor(db, **datos)
            try:
                c.guardar()
                print("Conductor guardado.")
            except Exception as e:
                print("Error guardando conductor:", e)
        elif opc == "2":
            idc = input("Ingrese identificación: ").strip()
            fila = Conductor.consultar_por_pk(con, idc)
            if not fila:
                print("No encontrado.")
            else:
                campos = dict(zip(Conductor.campos, fila))
                c = Conductor(db, **campos)
                c.mostrar_info()
        elif opc == "3":
            idc = input("Ingrese identificación: ").strip()
            fila = Conductor.consultar_por_pk(con, idc)
            if not fila:
                print("Conductor no existe.")
                continue
            print("Presione Enter para no modificar un campo.")
            # mostrar actuales
            for idx, campo in enumerate(Conductor.campos):
                print(f"{campo}: {fila[idx]}")
            nueva_dir = input(f"Direccion [{fila[3]}]: ").strip() or fila[3]
            nuevo_tel = input(f"Telefono [{fila[4]}]: ").strip() or fila[4]
            nuevo_correo = solicitar_correo_validado (f"Correo [{fila[5]}]: ").strip() or fila[5]
            nueva_ing = input(f"Fecha ingreso [{fila[7]}]: ").strip() or fila[7]
            nueva_retr = input(f"Fecha retiro [{fila[8]}]: ").strip() or fila[8]
            nuevo_val_adeuda = input(f"Valor a deuda [{fila[13]}]: ").strip() or fila[13]
            nuevo_total_ahorr = input(f"Total ahorrado [{fila[14]}]: ").strip() or fila[14]
            cur = con.cursor()
            cur.execute('''UPDATE infoConductor
                           SET direccion = ?, telefono = ?, correo = ?, fechaIngreso = ?, fechaRetiro = ?, valorAdeuda = ?, totalAhorrado = ?
                           WHERE identificacion = ?''',
                        (nueva_dir, nuevo_tel, nuevo_correo, nueva_ing, nueva_retr, nuevo_val_adeuda, nuevo_total_ahorr, idc))
            con.commit()
            print("Conductor actualizado.")
        elif opc == "0":
            break
        else:
            print("Opción inválida.")

# ---------- Menú Mantenimientos ----------
def menu_mantenimientos(con, db):
    while True:
        print("\n--- MANTENIMIENTOS ---")
        print("1. Registrar mantenimiento")
        print("2. Consultar por número de orden")
        print("3. Listar todos (sumatoria valores)")
        print("4. Consulta última fecha por placa")
        print("5. Actualizar registro (descripcion/valor/fecha)")
        print("6. Eliminar mantenimiento por número de orden")
        print("7. Consulta de la base de datos total de mantenimiento")
        print("0. Volver")
        opc = input("Opción: ").strip()
        if opc == "1":
            datos = leer_info_mantenimiento_input(con)
            m = Mantenimiento(db, **datos)
            try:
                m.guardar()
                print("Mantenimiento guardado.")
            except Exception as e:
                print("Error guardando mantenimiento:", e)
        elif opc == "2":
            num = input("Ingrese número de orden: ").strip()
            fila = Mantenimiento.consultar_por_pk(con, num)
            if not fila:
                print("No existe registro.")
            else:
                campos = dict(zip(Mantenimiento.campos, fila))
                m = Mantenimiento(db, **campos)
                m.mostrar_info()
        elif opc == "3":
            filas = Mantenimiento.listar_todos(con)
            total = Mantenimiento.suma_valores(con)
            print(f"Total mantenciones: {len(filas)}, suma valor facturado: {total}")
            for fila in filas:
                print(fila)
        elif opc == "4":
            placa = input("Ingrese placa: ").strip()
            try:
                maxf = Mantenimiento.max_fecha_por_placa(con, placa)
                print("Última fecha de servicio:", maxf)
            except Exception as e:
                print("Error:", e)
        elif opc == "5":
            num = input("Ingrese número de orden a actualizar: ").strip()
            cur = con.cursor()
            cur.execute("SELECT * FROM mantenimientoVehiculo WHERE numeroOrden=?", (num,))
            reg = cur.fetchone()
            if not reg:
                print("No existe.")
                continue
            print("Registro actual:", reg)
            nuevaDesc = input(f"Descripcion [{reg[4]}]: ").strip() or reg[4]
            nuevoValor = input(f"Valor [{reg[5]}]: ").strip() or reg[5]
            nuevaFecha = input(f"Fecha (DD/MM/YYYY) [{reg[6]}]: ").strip()
            if nuevaFecha != reg[6] and nuevaFecha != "":
                nuevaFecha = pedir_fecha("Ingrese nueva fecha (DD/MM/YYYY): ")
            else:
                nuevaFecha = reg[6]
            cur.execute('''UPDATE mantenimientoVehiculo
                           SET descripcionServicio = ?, valorFacturado = ?, fechaServicio = ?
                           WHERE numeroOrden = ?''', (nuevaDesc, nuevoValor, nuevaFecha, num))
            con.commit()
            print("Registro actualizado.")
        elif opc == "6":
            num = input("Ingrese número de orden a eliminar: ").strip()
            fila = Mantenimiento.consultar_por_pk(con, num)
            if not fila:
                print("No existe.")
                continue
            confirmar = input(f"¿Eliminar mantenimiento {num}? (s/n): ").strip().lower()
            if confirmar == "s":
                Mantenimiento.borrar_por_numero(con, num)
                print("Eliminado.")
            else:
                print("Cancelado.")
        elif opc== "7":
            qtable(con)
        elif opc == "0":
            break
        else:
            print("Opción inválida.")

# ---------------------------
# Generación de PDF: ficha integrada de vehículo
# ---------------------------
def generar_ficha_vehiculo_pdf(con):
    if not REPORTLAB_AVAILABLE:
        print("Reportlab no está instalado. Instale con: pip install reportlab")
        return
    placa = input("Ingrese la placa del vehículo para la ficha: ").strip()
    fila = Vehiculo.consultar_por_pk(con, placa)
    if not fila:
        print("Vehículo no encontrado.")
        return
    # obtener último mantenimiento
    ultima_fecha = Mantenimiento.max_fecha_por_placa(con, placa)
    # armar contenido
    estilos = getSampleStyleSheet()
    doc_name = f"Ficha_Vehiculo_{placa}.pdf"
    doc = SimpleDocTemplate(doc_name, pagesize=letter)
    story = []
    story.append(Paragraph(f"Ficha integrada - Vehículo {placa}", estilos['Title']))
    story.append(Spacer(1, 12))
    # datos vehiculo
    for i, campo in enumerate(Vehiculo.campos):
        story.append(Paragraph(f"<b>{campo}:</b> {fila[i]}", estilos['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Último mantenimiento:</b> {ultima_fecha}", estilos['Normal']))
    doc.build(story)
    print(f"PDF generado: {os.path.abspath(doc_name)}")

# ---------------------------
# Punto de entrada
# ---------------------------
def main():
    db = Database()
    con = db.conexion
    crear_tablas_todas(con)
    menu_principal(db)
    db.cerrar()

if __name__ == "__main__":
    main()

