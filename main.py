import pytracking
from fastapi import FastAPI, Response
import pymysql
import os
import pymysql.cursors

app = FastAPI()

def conexionBD():
    try:
        host_db = os.getenv('MYSQLHOST')
        user_db = os.getenv('MYSQLUSER')
        pass_db = os.getenv('MYSQLPASSWORD')
        db_name = os.getenv('MYSQLDATABASE')
        port_env = os.getenv('MYSQLPORT')
       
        conexion = pymysql.connect(
            host=host_db,      
            user=user_db,     
            password=pass_db, 
            database=db_name, 
            port=port_env, 
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conexion
    except Exception as e:
        print(f"Error real de conexión: {e}")
        return None

def insertarTrack(conexion, email, campaña):
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO track (email, campaña, fecha) VALUES (%s, %s, NOW())"
        cursor.execute(sql, (email, campaña))
        conexion.commit()
    except pymysql.err.MySQLError as e:
        print(f"Error: al insertar en la base de datos: {e}")

@app.get("/track/visualizacion/{data}")
def track_open(data: str):
    # Decodifica automáticamente el dato pasado en la URL
    result = pytracking.get_open_tracking_result(data)

    email_cliente = result.metadata.get("email")
    campaña = result.metadata.get("campaña")

    # Base de datos
    conexion = conexionBD()
    if not conexion:
        return Response(status_code=500)

    # Insertamos directamente el registro en track
    insertarTrack(conexion, email_cliente, campaña)
    conexion.close()

    # Devolvemos el píxel de tracking
    pixel_data, mime_type = pytracking.get_open_tracking_pixel()
    return Response(content=pixel_data, media_type=mime_type)
