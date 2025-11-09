import sqlite3
from sqlite3 import Error
from datetime import datetime
def conexionDB():
    try:
        con=sqlite3.connect('BDTaxisLaNacional.db')
        # creamos un objeto de conexión con que crea el repositorio
        # físico de la base de datos (archivo físico)
        return con
    except Error:
        print(Error)

def cerrarBD(con):
    con.close()

def pedirFecha(mensaje):
    while True:
        fechaStr = input(mensaje)
        try:
            fechaDt = datetime.strptime(fechaStr,"%Y/%m/%d").date()
            return fechaDt.strftime("%Y/%m/%d")
        except ValueError:
            print("Formato invalido. use AAAA/MM/DD")
    
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

def leerInfoVehiculo():
    placa=input("Placa vehiculo: ")
    marca=input("Marca: ")
    referencia=input("Referencia: ")
    modelo=input("Modelo: ")
    numeroChasis=input("Numero Chasis: ")
    numeroMotor=input("Numero de motor: ")
    color=input("Color: ")
    concesionario=input("Concensionario: ")
    fechaCompra= pedirFecha ("Fecha de compra: ")
    tiempoGarantia=input("Tiempo garantia: ")
    fechaCompraPoliza= pedirFecha("Fecha compra poliza ")
    proveedorPoliza=input("Proveedor poliza: ")
    fechaCompraSeguroOblig= pedirFecha("Fecha de compra seguro: ")
    proveedorSeguroOblig=input("Proveedor de seguro: ")
    indicadorActivo=input("Estado del vehiculo: ")
    vehiculo=(placa,marca,referencia,modelo,numeroChasis,numeroMotor,color,concesionario,fechaCompra,tiempoGarantia,fechaCompraPoliza,proveedorPoliza,fechaCompraSeguroOblig,proveedorSeguroOblig,indicadorActivo)
    print("La tupla vehiculo es; ",vehiculo)
    return vehiculo
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
                                fechaIngreso date NOT NULL,
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
    cursorObj=con.cursor()
    cursorObj.execute('''INSERT INTO infoConductor
                         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',duct)
    con.commit()

def leerInfoConductor():
    noConductor=input("Identificacion Conductor: ")
    nombre=input("Nombre: ")
    apellido=input("Apellido: ")
    direccion=input("Direccion: ")
    telefono=input("Telefono: ")
    correo=input("Correo: ")
    placaVehiculo=input("Placa vehiculo: ")
    fecIngreso=pedirFecha("Fecha de ingreso: ")
    fecRetiro=pedirFecha("Fecha de retiro: ")
    indContrato=input("Indicador contrato: ")
    turno=input("Turno: ")
    valorTurno=input("Valor del turno: ")
    valorAhorro=input("Valor Ahorro: ")
    valorAdeuda=input("Valor a deuda: ")
    totalAhorrado=input("Total Ahorrado: ")
    conductor=(noConductor,nombre,apellido,direccion,telefono,correo,placaVehiculo,fecIngreso,fecRetiro,indContrato,turno,valorTurno,valorAhorro,valorAdeuda,totalAhorrado)
    print("La tupla conductor es; ",conductor)
    return conductor
    
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

def leerInfoMantenimiento():
    noOrden=input("Numero de Orden: ")
    plVehiculo=input("Placa: ")
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
                                2- Actualizar informacion de vehiculo
                                3- Consultar informacion de un vehiculo
                                4- Actualizar informacion polizas de seguro
                                5- Retornar al menu principal

                                Seleccione una opccion: >>>''')
                if (opcVehiculos=='1'):
                    miVehiculo=leerInfoVehiculo()
                    crearVehiculo(con,miVehiculo)
                elif (opcVehiculos=='2'):
                    salirVehiculos=True
                elif (opcVehiculos=='3'):
                    salirVehiculos=True
                elif (opcVehiculos=='4'):
                    salirVehiculos=True
                elif (opcVehiculos=='5'):
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
                    miConductor=leerInfoConductor()
                    crearConductor(con,miConductor)
                elif (opcConductores=='2'):
                    salirConductores=True
                elif (opcConductores=='3'):
                    salirConductores=True
                elif (opcConductores=='4'):
                    salirConductores=True
        elif (opcPrincipal=='3'):
            salirMantenimientos=False
            while not salirMantenimientos:
                opcMantenimientos=input('''
                                 MENU DE MANTENIMIENTOS

                                 1- Crear un mantenimiento
                                 2- Consultar mantenimiento realizado
                                 3- Borrar mantenimiento
                                 4- Retornar al menu principal

                                 Seleccione una opcion: >>> ''')
                if (opcMantenimientos=='1'):
                    miMantenimiento=leerInfoMantenimiento()
                    crearMantenimiento(con,miMantenimiento)
                elif (opcMantenimientos=='2'):
                    consultarMantenimientoRealizado1(con)
                elif (opcMantenimientos=='3'):
                    borrarMantenimiento(con)
                elif (opcMantenimientos=='4'):
                    salirMantenimientos=True

        elif (opcPrincipal=='4'):
            salirPrincipal=True
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
    #crearConductor(con,duct)
    #leerInfoConductor()
    #cerrarDB(miCon)
    
main()
