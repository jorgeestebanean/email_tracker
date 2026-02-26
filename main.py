
import pytracking
from fastapi import FastAPI, Response, Request
import pymysql
import os
import pymysql.cursors

app = FastAPI()


def conexionBD():
    try:
        # Forzamos la lectura de Railway. Si os.getenv falla, no conectará a nada.
        host_db = os.getenv('MYSQLHOST')
        user_db = os.getenv('MYSQLUSER')
        pass_db = os.getenv('MYSQLPASSWORD')
        db_name = os.getenv('MYSQLDATABASE')
        port_db = int(os.getenv('MYSQLPORT', 3306))
        puerto = int(port_env) if port_env and port_env.strip() else 3306

        print(f"DEBUG: Intentando conectar a {host_db}...") # Esto saldrá en tus logs

        conexion = pymysql.connect(
            host=host_db,      
            user=user_db,     
            password=pass_db, 
            database=db_name, 
            port=puerto, 
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conexion
    except Exception as e:
        print(f"Error real de conexión: {e}")
        return None

def insertarCampaña(conexion,campaña):
    try:
       cursor = conexion.cursor()
       sql = "INSERT IGNORE INTO campaña (nombre) VALUES (%s)"
       cursor.execute(sql, (campaña,))
       conexion.commit()
    except pymysql.err.MySQLError as e:
        print(f"Error: al insertar en la base de datos: {e}")

    

def existeCampaña(conexion,campaña):
    try:
        cursor = conexion.cursor()
        sql = "SELECT id FROM campaña WHERE nombre = %s"
        cursor.execute(sql, (campaña,))
        result = cursor.fetchone()
        return result["id"] if result else None
    except pymysql.err.MySQLError as e:
        print(f"Error: al consultar la base de datos: {e}")
        return None

def insertarTrack(conexion,email,campaña_id):
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO track (email, campaña_id, fecha) VALUES (%s, %s, NOW())"
        cursor.execute(sql, (email, campaña_id))
        conexion.commit()
    except pymysql.err.MySQLError as e:
        print(f"Error: al insertar en la base de datos: {e}")

@app.get("/track/visualizacion/{data}")
def track_open(data: str):
    # Descodifica automáticamente el dato pasado en la URL
    result = pytracking.get_open_tracking_result(data)

    email_cliente = result.metadata.get("email")
    campaña = result.metadata.get("campaña")

    # Base de datos
    conexion = conexionBD()
    if not conexion:
        return Response(status_code=500)
    id_campaña = existeCampaña(conexion, campaña)
    if not id_campaña:
        insertarCampaña(conexion, campaña)
        id_campaña = existeCampaña(conexion, campaña)

    insertarTrack(conexion, email_cliente, id_campaña)
    
    conexion.close()

    # Usamos la función de la librería para devolver el píxel perfecto
    pixel_data, mime_type = pytracking.get_open_tracking_pixel()
    return Response(content=pixel_data, media_type=mime_type)
