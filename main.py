import pytracking
from fastapi import FastAPI, Response, Request
app = FastAPI()
 

@app.get("/track/visualizacion/{data}")
def track_open(data: str):
    # Descodifica automáticamente el dato pasado en la URL
    result = pytracking.get_open_tracking_result(data)
    
    email_cliente = result.metadata.get("email")
    campaña = result.metadata.get("campaña")
    print(f"Correo abierto por: {email_cliente}")
    print(f"Campaña: {campaña}")

    # Guardamos fichero con los correos abiertos 
    with open("emails_abiertos.txt", "a") as f:
        f.write(f"{email_cliente}\n")

    # Usamos la función de la librería para devolver el píxel perfecto
    pixel_data, mime_type = pytracking.get_open_tracking_pixel()
    return Response(content=pixel_data, media_type=mime_type)
