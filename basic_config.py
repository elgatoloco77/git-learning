import serial
import time
import pandas as pd
import re

def leer_todo(ser, espera=2.0):
    time.sleep(espera)
    salida = ""
    while True:
        chunk = ser.read(1024).decode(errors="ignore")
        if not chunk:
            break
        salida += chunk
        if "--More--" in chunk:
            ser.write(b" ")
            time.sleep(0.3)
    if ser.in_waiting:
        salida += ser.read(ser.in_waiting).decode(errors="ignore")
    return salida

def obtener_modelo_serie(ser):
    ser.write(b"\n")               
    time.sleep(0.5)
    ser.write(b"terminal length 0\n") 
    time.sleep(0.5)

    ser.write(b"show inventory\n")
    salida = leer_todo(ser, espera=2.0)

    m_modelo = re.search(r"PID:\s*([\w\-/\.]+)", salida, re.IGNORECASE)
    m_serie  = re.search(r"SN:\s*([\w\-]+)", salida, re.IGNORECASE)

    modelo = m_modelo.group(1) if m_modelo else None
    serie  = m_serie.group(1)  if m_serie  else None

    return modelo, serie, salida

def configurar_dispositivo(ser, nombre, usuario, contrasena, dominio):
    comandos = [
        "configure terminal",
        f"hostname {nombre}",
        f"username {usuario} password {contrasena}",
        f"ip domain-name {dominio}",
        "crypto key generate rsa",
    ]
    for cmd in comandos:
        ser.write((cmd + "\n").encode())
        time.sleep(1)

    ser.write(b"1024\n")
    time.sleep(2)

    extra_cmds = [
        "ip ssh version 2",
        "line console 0",
        "login local",
        "line vty 0 4",
        "login local",
        "transport input ssh",
        "transport output ssh",
        "end",
        "write memory"
    ]
    for cmd in extra_cmds:
        ser.write((cmd + "\n").encode())
        time.sleep(0.7)

    print(f" Configuración aplicada a {nombre}")

def cargar_y_configurar():
    ruta_excel = r"C:\Users\52675\Desktop\dispositivos_ejemplo Alejandro.xlsx"
    df = pd.read_excel(ruta_excel)

    columnas = {"modelo", "serie", "puerto", "baudios", "nombre", "usuario", "contrasena", "dominio"}
    if not columnas.issubset(df.columns):
        raise ValueError(f"El Excel debe tener las columnas: {columnas}")

    for _, fila in df.iterrows():
        puerto   = str(fila["puerto"])
        baudios  = int(fila["baudios"])

        try:
            print(f"\n Conectando al {puerto}...")
            ser = serial.Serial(puerto, baudios, timeout=2)
            time.sleep(2)

            modelo_real, serie_real, salida = obtener_modelo_serie(ser)
            print(f" Modelo detectado: {modelo_real}, Serie: {serie_real}")

            if (modelo_real and serie_real and
                modelo_real == str(fila["modelo"]) and
                serie_real  == str(fila["serie"])):
                print(" Coincidencia , configurando...")
                configurar_dispositivo(
                    ser,
                    str(fila["nombre"]),
                    str(fila["usuario"]),
                    str(fila["contrasena"]),
                    str(fila["dominio"])
                )
            else:
                print(" No coincide ,  no se configuración.")
                print("Salida completa de 'show inventory':\n", salida)

            ser.close()

        except Exception as e:
            print(f" Error en {puerto}: {e}")

if __name__ == "__main__":
    cargar_y_configurar()
