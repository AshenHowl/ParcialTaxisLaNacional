import sqlite3
from sqlite3 import Error
from datetime import datetime
import os
# --- IMPORTS PARA GENERAR PDF ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def conexionDB():
    try:
        con=sqlite3.connect('BDTaxisLaNacional.db')
        print("Base de datos", os.path.abspath("TaxisLaNacional.db"))
        # creamos un objeto de conexión con que crea el repositorio
        # físico de la base de datos (archivo físico)
        return con
    except Error:
        print(Error)

def cerrarBD(con):
    con.close()

def pedirFecha(mensaje):
    while True:
        fecha_str = input(mensaje)  
        try:
            # Convertimos de DD/MM/YYYY a datetime.date
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            # Retornamos como string AAAA-MM-DD para la BD
            return fecha_obj.strftime("%Y-%m-%d")
        except ValueError:
            print("Formato inválido. Debe ser DD/MM/YYYY.")


    
#============================================================================================
#----------------------------VEHICULOS-------------------------------------------------------
#============================================================================================

def crearTablaVehiculos(con):
    cursorObj=con.cursor()
    #1.  Es un objeto que recorre toda el repositorio de
    #base de datos.  Utiliza para ello el objeto de conexión
    #que ya habíamos creado.
    cad='''CREATE TABLE IF NOT EXISTS infoVehiculos(
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
                                PRIMARY KEY(placa))'''
    #2.  Creamos la cadena con el SQL a ejecutar
    cursorObj.execute(cad)
    #3.  Ejecutamos la cadena
    con.commit()
    #4. Asegurar la persistencia:  llamamos al método commit()
    #del objeto conexión

def crearVehiculo(con,duct):    
    cursorObj=con.cursor()
    cursorObj.execute('''INSERT INTO infoVehiculos
                         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',duct)
    con.commit()

def validarEstado(mensaje):
    while True:
        indicadorActivo = input(mensaje)
        if indicadorActivo in ["1","2"]:
            return indicadorActivo
        else:
            print("Estado invalido. Por favor seleccione Activo[1] Inactivo[2] ")

def leerInfoVehiculo():
    placa=input("Placa vehiculo: ")
    marca=input("Marca: ")
    referencia=input("Referencia: ")
    modelo=input("Modelo: ")
    numeroChasis=input("Numero Chasis: ")
    numeroMotor=input("Numero de motor: ")
    color=input("Color: ")
    concesionario=input("Concesionario: ")
    fechaCompra= pedirFecha ("Fecha de compra: ")
    tiempoGarantia=input("Tiempo garantia: ")
    fechaCompraPoliza= pedirFecha("Fecha compra poliza ")
    proveedorPoliza=input("Proveedor poliza: ")
    fechaCompraSeguroOblig= pedirFecha("Fecha de compra seguro: ")
    proveedorSeguroOblig=input("Proveedor de seguro: ")
    indicadorActivo=validarEstado("Estado: Activo[1] Inactivo[2])")
    vehiculo=(placa,marca,referencia,modelo,numeroChasis,numeroMotor,color,concesionario,fechaCompra,tiempoGarantia,fechaCompraPoliza,proveedorPoliza,fechaCompraSeguroOblig,proveedorSeguroOblig,indicadorActivo)
    return vehiculo

def validarPlaca(con, mensaje):
    cursorObj = con.cursor()
    while True:
        placa=input(mensaje)
        cursorObj.execute("SELECT * FROM infoVehiculos WHERE placa=?", (placa,))
        placaVehiculo = cursorObj.fetchone()

        if placaVehiculo is None:
            print("La placa ingresada no se encuentra registrada. Por favor ingrese una placa valida")
        else:
            print("Placa registrada")
            return placaVehiculo

def consultarVehiculo(con):
    veh = validarPlaca(con,"Ingrese el numero de placa a validar: ")
    print("----------------------------------------------------")
    print("Informacion asociada al vehiculo con numero de placa",veh[0])
    print("----------------------------------------------------")
    print("Marca:", veh[1])
    print("Referencia:", veh[2])
    print("Modelo:", veh[3])
    print("Numero de chasis:", veh[4])
    print("Numero de motor:", veh[5])
    print("Color:", veh[6])
    print("Concesionario:", veh[7])
    print("Fecha de compra:", veh[8])
    print("Garantia: ", veh[9],"meses")
    print("Fecha de compra poliza:", veh[10])
    print("Proveedor de poliza:", veh[11])
    print("Fecha de compra seguro:", veh[12])
    print("Proveedor de seguro:", veh[13])
    print("Estado del vehiculo:", veh[14])
    print("---------------------------")

def modificarPoliza(con):
    cursorObj = con.cursor()
    veh = validarPlaca(con, "Indique la placa del vehículo a modificar: ")
    placa = veh[0]
    fechaAnteriorPoliza = datetime.strptime(veh[10], "%Y-%m-%d").date()

    while True:
        nuevaFecComPoliza = pedirFecha("Ingrese nueva fecha de compra de la póliza (DD/MM/YYYY): ")
        nuevaFecComPolizaDate = datetime.strptime(nuevaFecComPoliza, "%Y-%m-%d").date()
        
        if nuevaFecComPolizaDate > fechaAnteriorPoliza:
            cursorObj.execute('''
                UPDATE infoVehiculos
                SET fechaCompraPoliza = ?
                WHERE placa = ?
            ''', (nuevaFecComPoliza, placa))
            con.commit()
            print("Póliza actualizada correctamente.")
            break
        else:
            print("La nueva fecha debe ser mayor que la fecha actual.")
            break
            

        
def modificarIndicador(con):
    cursorObj = con.cursor()
    veh = validarPlaca(con, "Indique el número de placa del vehículo a modificar: ")
    placa = veh[0]
    nuevoEstado = validarEstado("Nuevo estado: Activo[1] Inactivo[2]: ")

    cursorObj.execute('''
        UPDATE infoVehiculos
        SET activo = ?
        WHERE placa = ?
    ''', (nuevoEstado, placa))

    con.commit()
    print("Estado actualizado correctamente.")

#============================================================================================
#----------------------------CONDUCTORES-----------------------------------------------------
#============================================================================================

def crearTablaConductores(con):    
    cursorObj=con.cursor()
    cursorObj.execute('''CREATE TABLE IF NOT EXISTS infoConductor(
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

def crearConductor(con,duct):
    try:   
        cursorObj=con.cursor()
        cursorObj.execute('''INSERT INTO infoConductor
                             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',duct)
        con.commit()
        print("Conductor guardado con exito")
    except Excepcion as e:
        print("Error al guardar el conductor", e)
        
def validarConductor(con, mensaje):
    cursorObj = con.cursor()
    while True:
        identificacion=input(mensaje)
        cursorObj.execute("SELECT * FROM infoConductor WHERE identificacion=?", (identificacion,))
        idConductor = cursorObj.fetchone()

        if idConductor is None:
            print("La identificacion no se encuentra registrada. Porfavor indique una identificacion valida")
        else:
            print("Identificacion registrada")
            return idConductor

def validarContrato(fecIngreso,fecRetiro):
    while True:
        indicador = input("Indicador contrato: Contratado[1], No contratado[2], Despedido[3]: ")
        if indicador not in ["1","2","3"]:
            print("Por favor elija un estado valido: Contratado[1] No contratado[2] Despedido[3]")
            continue
        indicador=int(indicador)

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
            print("Error:Las fechas no coinciden con el estado seleccionado, intente de nuevo")
            print("Contratado = Fecha de ingreso pero no de salida")
            
def leerInfoConductor(con):
    noConductor=input("Identificacion Conductor: ")
    nombre=input("Nombre: ")
    apellido=input("Apellido: ")
    direccion=input("Direccion: ")
    telefono=input("Telefono: ")
    correo=input("Correo: ")
    placaVehiculo=validarPlaca(con,"Placa vehiculo: ")
    fecIngreso_str = input("Fecha de ingreso (DD/MM/YYYY), deje vacío si no aplica: ")
    if fecIngreso_str.strip():
        fecIngreso = pedirFecha("Fecha de ingreso (DD/MM/YYYY): ")
    else:
        fecIngreso = None

    fecRetiro_str = input("Fecha de retiro (DD/MM/YYYY), deje vacío si no aplica: ")
    if fecRetiro_str.strip():
        fecRetiro = pedirFecha("Fecha de retiro (DD/MM/YYYY): ")
    else:
        fecRetiro = None
    indContrato=validarContrato(fecIngreso,fecRetiro)
    turno=input("Turno: ")
    valorTurno=input("Valor del turno: ")
    valorAhorro=input("Valor Ahorro: ")
    valorAdeuda=input("Valor a deuda: ")
    totalAhorrado=input("Total Ahorrado: ")
    conductor=(noConductor,nombre,apellido,direccion,telefono,correo,placaVehiculo,fecIngreso,fecRetiro,indContrato,turno,valorTurno,valorAhorro,valorAdeuda,totalAhorrado)
    return conductor

def consultconductor(con):
    condr=validarConductor(con, "Ingrese el numero de identificacion del conductor: ")
    print("------------------------------------")
    print("La informacion asociada con el numero de identificacion es:",condr[0])
    print("Nombre: ",condr[1])
    print("Apellido: ",condr[2])
    print("Direccion: ",condr[3])
    print("Telefono: ",condr[4])
    print("Correo: ",condr[5])
    print("Placa de vehiculo: ",condr[6])
    print("Fecha de ingreso (si aplica): ",condr[7])
    print("Fecha de retiro (si aplica): ",condr[8])
    print("Indicador de contrato (1:Si, 2:No, 3:Despedido)",condr[9])
    print("Turno: ",condr[10])
    print("Valor de el turno: ",condr[11])
    print("Valor de ahorro: ",condr[12])
    print("Valor a deuda: ",condr[13])
    print("Total ahorrado: ",condr[14])

def actConduct(con):
    cursorObj = con.cursor()
    condr = validarConductor(con, "Ingrese el numero de identificacion del conductor: ")
     #Asumimos que el campo 0 es el id
    if condr is None:
        print("Conductor no registrado.")
        return
    id = condr[0]
    print("La informacion asociada con el numero de identificacion es:",condr[0])
    print("Nombre: ",condr[1])
    print("Apellido: ",condr[2])
    print("Direccion: ",condr[3])
    print("Telefono: ",condr[4])
    print("Correo: ",condr[5])
    print("Placa de vehiculo: ",condr[6])
    print("Fecha de ingreso (si aplica): ",condr[7])
    print("Fecha de retiro (si aplica): ",condr[8])
    print("Indicador de contrato (1:Si, 2:No, 3:Despedido)",condr[9])
    print("Turno: ",condr[10])
    print("Valor de el turno: ",condr[11])
    print("Valor de ahorro: ",condr[12])
    print("Valor a deuda: ",condr[13])
    print("Total ahorrado: ",condr[14])
    print("\n--- Actualización de campos ---")
    print("Presione Enter si no desea cambiar un campo.\n")
        # Pide nuevos valores o deja los actuales si no se escribe nada
    #n_nombre=input(f"Nombre: [{condr[1]}]: ") or condr[1]
    #n_apellido=input(f"Apellido: [{condr[2]}]: ") or condr[2]
    n_direccion=input(f"Direccion: [{condr[3]}]: ") or condr[3]
    n_telefono=input(f"Telefono: [{condr[4]}]: ") or condr[4]
    n_correo=input(f"Correo: [{condr[5]}]: ") or condr[5]
    #n_pl_veh=input(f"Placa de vehiculo: [{condr[6]}]: ") or condr[6]
    n_fh_ingreso=input(f"Fecha de ingreso: [{condr[7]}]: ") or condr[7]
    n_fh_retr=input(f"Fecha de retiro: [{condr[8]}]: ") or condr[8]
    #n_ind_contrat=input(f"Indicador de contrato: [{condr[9]}]: ") or condr[9]
    #n_turn=input(f"Turno: [{condr[10]}]: ") or condr[10]
    #n_val_turn=input(f"Valor de el turno: [{condr[11]}]: ") or condr[11]
    #n_val_ahrro=input(f"Valor de ahorro: [{condr[12]}]: ") or condr[12]
    n_val_deuda=input(f"Valor a deuda: [{condr[13]}]: ") or condr[13]
    n_tl_ahrrdo=input(f"Total ahorrado: [{condr[14]}]: ") or condr[14]
         # Ejecutar actualización
    cursorObj.execute('''
        UPDATE infoConductor
        SET direccion = ?, telefono = ?, correo = ?, fechaIngreso = ?, fechaRetiro = ?, valorAdeuda = ?, totalAhorrado = ?
        WHERE identificacion = ?
        ''', (n_direccion, n_telefono, n_correo, n_fh_ingreso, n_fh_retr, n_val_deuda, n_tl_ahrrdo, id ))    
    con.commit()
    print("Registro actualizado correctamente.")
    
#============================================================================================
#----------------------------MANTENIMIENTO---------------------------------------------------
#============================================================================================

def crearTablaMantenimientos(con):     
    cursorObj=con.cursor()
    cursorObj.execute('''CREATE TABLE IF NOT EXISTS mantenimientoVehiculo(
                                numeroOrden integer NOT NULL,
                                placaVehiculo text NOT NULL, 
                                nit text NOT NULL,
                                nombreProveedor text NOT NULL,
                                descripcionServicio text NOT NULL,
                                valorFacturado integer NOT NULL,
                                fechaServicio date NOT NULL,
                                PRIMARY KEY(numeroOrden))''')
    con.commit()

def leerInfoMantenimiento(con):
    noOrden=input("Numero de Orden: ")
    plVehiculo=validarPlaca(con,"Placa: ")
    n=input("Nit Proveedor: ")
    nomProveedor=input("Nombre Proveedor: ")
    desServicio=input("Servicio Recibio: ")
    ValFacturado=input("Valor Facturado: ")
    fecServicio=pedirFecha("Fecha manteminiento: ")
    mantenimiento=(noOrden,plVehiculo,n,nomProveedor,desServicio,ValFacturado,fecServicio)
    print("La tupla mantenimiento es; ",mantenimiento)
    return mantenimiento

def crearMantenimiento(con,mant):    
    cursorObj=con.cursor()
    cursorObj.execute('''INSERT INTO mantenimientoVehiculo
                         VALUES(?,?,?,?,?,?,?)''',mant)
    con.commit()

def actualizarMantenimientoRealizado(con):
    cursorObj = con.cursor()
    noOrden = input("Ingrese el número de orden que desea actualizar: ")

    cursorObj.execute("SELECT * FROM mantenimientoVehiculo WHERE numeroOrden=?", (noOrden,))
    registro = cursorObj.fetchone()

    if registro is None:
        print("No existe un mantenimiento con el número de orden ingresado.")
        return

    print("Registro encontrado:")
    print("Número de orden:", registro[0])
    print("Placa vehículo:", registro[1])
    print("Nit:", registro[2])
    print("Nombre proveedor:", registro[3])
    print("Descripción servicio:", registro[4])
    print("Valor facturado:", registro[5])
    print("Fecha servicio:", registro[6])

    print("\n--- Actualización de campos ---")
    print("Presione Enter si no desea cambiar un campo.\n")

    # Pide nuevos valores o deja los actuales si no se escribe nada
    nuevaDescripcion = input(f"Descripción del servicio [{registro[4]}]: ") or registro[4]
    nuevoValor = input(f"Valor facturado [{registro[5]}]: ") or registro[5]
    nuevaFecha = input(f"Fecha del servicio (dd/mm/aaaa) [{registro[6]}]: ") or registro[6]

    # Ejecutar actualización
    cursorObj.execute('''
        UPDATE mantenimientoVehiculo
        SET descripcionServicio = ?, valorFacturado = ?, fechaServicio = ?
        WHERE numeroOrden = ?
    ''', (nuevaDescripcion, nuevoValor, nuevaFecha, noOrden))

    con.commit()
    print("Registro actualizado correctamente.")

def consultarMantenimientoRealizado(con):
    cursorObj=con.cursor()
    cad='SELECT numeroOrden,placaVehiculo,nombreProveedor,descripcionServicio,valorFacturado,fechaServicio FROM mantenimientoVehiculo WHERE numeroOrden='+noOrden
    cursorObj.execute(cad)
    filas=cursorObj.fetchall()
    print("El tipo de dato de filas es: ",type(filas))
    for row in filas:
        no=row[0]
        placa=row[1]
        ValorFacturado=row[5]
        descripcion=row[4]
        nombreP=row[3]
        fechaS=row[6]
        ni=[2]
        print("Orden: ",no,"Placa: ",placa,"Fecha: ",fechaS)
    #print("Orden: ",no,"Placa: ",placa,"Fecha: ",fechaS)

def consultarMantenimientoRealizado1(con):
    
    noOrden = input("Ingrese el número de orden a consultar: ")
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM mantenimientoVehiculo WHERE numeroOrden=?", (noOrden,))
    filas = cursorObj.fetchall()

    if not filas:
        print("No se encontró ningún mantenimiento con ese número de orden.")
        return

    print("Resultados encontrados:")
    for row in filas:
        print("Orden:", row[0])
        print("Placa:", row[1])
        print("NIT Proveedor:", row[2])
        print("Nombre Proveedor:", row[3])
        print("Descripción Servicio:", row[4])
        print("Valor Facturado:", row[5])
        print("Fecha Servicio:", row[6])
        print("---------------------------")


def consultarMantenimientoRealizado2(con):
    cursorObj=con.cursor()
    cad='SELECT * FROM mantenimientoVehiculo'
    cursorObj.execute(cad)
    filas=cursorObj.fetchall()
    print("El tipo de dato de filas es: ",type(filas))
    for row in filas:
        sumatoriaValorFacturado=row[0]
        print("El valor facturado total es: ",sumatoriaValorFacturado)
    #print("Orden: ",no,"Placa: ",placa,"Fecha: ",fechaS)

def consultarMantenimientoRealizado3(con):
    cursorObj=con.cursor()
    cad='SELECT max(FechaServicio) FROM mantenimientoVehiculo WHERE placaVehiculo="'+placa+'"'
    cursorObj.execute(cad)
    filas=cursorObj.fetchall()
    print("El tipo de dato de filas es: ",type(filas))
    for row in filas:
        maximafechaServicio=row[0]
        print("La maxima fecha de servicio es: ",maximafechaServicio)
    #print("Orden: ",no,"Placa: ",placa,"Fecha: ",fechaS)
    
    def borrarMantenimiento(con):
        cursorObj = con.cursor()
    noOrden = input("Ingrese el número de orden que desea eliminar: ")

    cursor.execute("SELECT * FROM mantenimientoVehiculo WHERE numeroOrden=?", (noOrden,))
    registro = cursor.fetchone()

    if registro is None:
        print("No existe un mantenimiento con ese número de orden.")
        return

    confirmar = input(f"¿Está seguro de eliminar el mantenimiento {noOrden}? (s/n): ")

    if confirmar.lower() == "s":
        cursor.execute("DELETE FROM mantenimientoVehiculo WHERE numeroOrden=?", (noOrden,))
        con.commit()
        print("Mantenimiento eliminado correctamente.")
    else:
        print("Eliminación cancelada.")




#============================================================================================
#----------------------------PDF------------------------------------------------------------
#============================================================================================
def generarFichaVehiculoPDF(con):
    cursor = con.cursor()

    placa = input("Ingrese la placa del vehículo para generar la ficha en PDF: ")

    #--------------------------------------------
    # 1. CONSULTAR VEHÍCULO
    #--------------------------------------------
    cursor.execute("SELECT * FROM infoVehiculos WHERE placa=?", (placa,))
    veh = cursor.fetchone()

    if veh is None:
        print("No existe un vehículo con esa placa.")
        return

    #--------------------------------------------
    # 2. CONSULTAR CONDUCTOR ASIGNADO
    #--------------------------------------------
    cursor.execute("SELECT nombre, apellido, telefono, correo, fechaIngreso, fechaRetiro, indicadorContratado "
                   "FROM infoConductor WHERE placaVehiculo=?", (placa,))
    conductor = cursor.fetchone()

    #--------------------------------------------
    # 3. CONSULTAR ÚLTIMO MANTENIMIENTO
    #--------------------------------------------
    cursor.execute("""
        SELECT descripcionServicio, valorFacturado, fechaServicio, nombreProveedor
        FROM mantenimientoVehiculo
        WHERE placaVehiculo=?
        ORDER BY fechaServicio DESC
        LIMIT 1
    """, (placa,))
    mantenimiento = cursor.fetchone()

    #--------------------------------------------
    # 4. CREAR PDF
    #--------------------------------------------
    filename = f"FichaVehiculo_{placa}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()
    Story = []

    # Título
    Story.append(Paragraph(f"<b>FICHA DE VEHÍCULO - {placa}</b>", styles["Title"]))
    Story.append(Spacer(1, 12))

    #--------------------------------------------
    # TABLA: Información del Vehículo
    #--------------------------------------------
    veh_tabla = [
        ["Campo", "Valor"],
        ["Placa", veh[0]],
        ["Marca", veh[1]],
        ["Referencia", veh[2]],
        ["Modelo", veh[3]],
        ["Número de Chasis", veh[4]],
        ["Número de Motor", veh[5]],
        ["Color", veh[6]],
        ["Concesionario", veh[7]],
        ["Fecha de Compra", veh[8]],
        ["Garantía (meses)", veh[9]],
        ["Fecha Compra Póliza", veh[10]],
        ["Proveedor Póliza", veh[11]],
        ["Fecha SOAT", veh[12]],
        ["Proveedor SOAT", veh[13]],
        ["Activo (1=Sí / 2=No)", veh[14]]
    ]

    tablaVeh = Table(veh_tabla, colWidths=[180, 300])
    tablaVeh.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ]))

    Story.append(Paragraph("<b>Información del Vehículo</b>", styles["Heading2"]))
    Story.append(tablaVeh)
    Story.append(Spacer(1, 15))

    #--------------------------------------------
    # TABLA: Información del Conductor
    #--------------------------------------------
    Story.append(Paragraph("<b>Información del Conductor Asignado</b>", styles["Heading2"]))

    if conductor:
        cond_tabla = [
            ["Campo", "Valor"],
            ["Nombre", conductor[0] + " " + conductor[1]],
            ["Teléfono", conductor[2]],
            ["Correo", conductor[3]],
            ["Fecha Ingreso", conductor[4]],
            ["Fecha Retiro", conductor[5]],
            ["Estado (1=Sí, 2=No, 3=Despedido)", conductor[6]]
        ]
    else:
        cond_tabla = [["No hay conductor asignado.", ""]]

    tablaCond = Table(cond_tabla, colWidths=[180, 300])
    tablaCond.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))

    Story.append(tablaCond)
    Story.append(Spacer(1, 15))

    #--------------------------------------------
    # TABLA: Último Mantenimiento
    #--------------------------------------------
    Story.append(Paragraph("<b>Último Mantenimiento Registrado</b>", styles["Heading2"]))

    if mantenimiento:
        man_tabla = [
            ["Campo", "Valor"],
            ["Descripción", mantenimiento[0]],
            ["Valor Facturado", mantenimiento[1]],
            ["Fecha", mantenimiento[2]],
            ["Proveedor", mantenimiento[3]]
        ]
    else:
        man_tabla = [["No hay mantenimientos registrados.", ""]]

    tablaMant = Table(man_tabla, colWidths=[180, 300])
    tablaMant.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))

    Story.append(tablaMant)
    Story.append(Spacer(1, 20))

    #--------------------------------------------
    # GENERAR PDF
    #--------------------------------------------
    doc.build(Story)
    print(f"PDF generado exitosamente: {filename}")

#============================================================================================
#----------------------------MENU------------------------------------------------------------
#============================================================================================

def menu(con):

    salirPrincipal=False
    while not salirPrincipal:
        opcPrincipal=input('''
                    MENU PRINCIPAL TAXIS LA NACIONAL

                    1- Menu de gestion de Vehiculos
                    2- Menu de gestion de Conductores
                    3- Menu de gestion de Mantenimientos
                    4- Ficha de Vehiculo
                    5- Salir

                    Selecciones una opcion: >>> ''')
        if (opcPrincipal=='1'):
            salirVehiculos=False
            while not salirVehiculos:
                opcVehiculos=input('''
                                MENU DE ADMINISTRACION DE VEHICULOS

                                1- Crear un nuevo vehiculo
                                2- Consultar informacion de un vehiculo
                                3- Actualizar informacion de vehiculo
                                4- Retornar al menu principal

                                Seleccione una opcion: >>>''')
                if (opcVehiculos=='1'):
                    miVehiculo=leerInfoVehiculo()
                    crearVehiculo(con,miVehiculo)
                elif (opcVehiculos=='2'):
                    consultarVehiculo(con)
                elif (opcVehiculos=='3'):
                    salirActVehiculos=False
                    while not salirActVehiculos:
                        opcActVehiculos=input('''
                                MENU DE ADMINISTRACION DE ACTUALIZACION DE VEHICULOS
                                ¿QUE DESEA MODIFICAR?
                                
                                1- Estado del vehiculo
                                2- Informacion de la poliza de seguro
                                3- Retornar al menu de administracion de vehiculos

                                Seleccione una opccion: >>>''')
                        if(opcActVehiculos=='1'):
                            modificarIndicador(con)
                        elif(opcActVehiculos=='2'):
                            modificarPoliza(con)
                        elif(opcActVehiculos=='3'):
                            salirActVehiculos=True
                elif (opcVehiculos=='4'):
                    salirVehiculos=True
                        

            
        elif (opcPrincipal=='2'):
            salirConductores=False
            while not salirConductores:
                opcConductores=input('''
                                MENU DE ADMINISTRACION DE CONDUCTORES

                                1- Crear un nuevo conductor
                                2- Actualizar informacion conductor
                                3- Consultar informacion de un conductor
                                4- Retornar al menu principal

                                Seleccione una opccion: >>>''')
                if (opcConductores=='1'):
                    miConductor=leerInfoConductor(con)
                    crearConductor(con,miConductor)
                elif (opcConductores=='2'):
                    actConduct(con)
                elif (opcConductores=='3'):
                    consultconductor(con)
                elif (opcConductores=='4'):
                    salirConductores=True
                    
        elif (opcPrincipal=='3'):
            salirMantenimientos=False
            while not salirMantenimientos:
                opcMantenimientos=input('''
                                 MENU DE MANTENIMIENTOS

                                 1- Crear un mantenimiento
                                 2- Consultar mantenimiento realizado
                                 3- Retornar al menu principal

                                 Seleccione una opcion: >>> ''')
                if (opcMantenimientos=='1'):
                    miMantenimiento=leerInfoMantenimiento(con)
                    crearMantenimiento(con,miMantenimiento)
                elif (opcMantenimientos=='2'):
                    consultarMantenimientoRealizado1(con)
                elif (opcMantenimientos=='3'):
                    salirMantenimientos=True

        elif (opcPrincipal=='4'):
            generarFichaVehiculoPDF(con)
            
        elif (opcPrincipal=='5'):
            salirPrincipal=True

def main():
    miCon=conexionDB()
    crearTablaVehiculos(miCon)
    crearTablaConductores(miCon)
    crearTablaMantenimientos(miCon)
    menu(miCon)
    #crearTablaVehiculos1(miCon)
    #insertarVehiculos(miCon)
    #crearTablaMantenimiento(miCon)
    #miMantenimiento=leerInfoMantenimiento()
    #crearMantenimiento(miCon,miMantenimiento)
    #actualizarMantenimiento(miCon)
    #consultarMantenimientoRealizado(miCon)
    #consultarMantenimientoRealizado1(miCon)
    #consultarMantenimientoRealizado2(miCon)
    #consultarMantenimientoRealizado3(miCon)
    #borrarMantenimiento(miCon)
    #borrarTablaVehiculos(miCon)
    #crearTablaConductor(miCon)
    #cc=leerInfoConductor()
    #crearConductor(con,cc)
    
    
    #leerInfoConductor()
    #cerrarDB(miCon)
    
main()
