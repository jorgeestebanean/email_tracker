
import pytracking
from fastapi import FastAPI, Response, Request
import pymysql

app = FastAPI()


def conexionBD():
    try:
        conexion = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="email_tracker",
            cursorclass=pymysql.cursors.DictCursor,
        )

    except pymysql.err.OperationalError as e:
        print(f"Error: al conectar a la base de datos: {e}")
        return None

    except pymysql.err.InternalError as e:
        print(f"Error: no se ha encontrado la base de datos: {e}")
        return None

    return conexion

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
