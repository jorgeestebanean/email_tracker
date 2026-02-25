import pytracking
from fastapi import FastAPI, Response, Request
#cd C:\Users\Jorge Esteban Garcia\Desktop\DAO\ejemplo_mailjet\
#.venv\Scripts\Activate
#uvicorn endpoint:app --host 0.0.0.0 --port 8080 --reload
app = FastAPI()
 

@app.get("/track/visualizacion/{data}")
def track_open(data: str):
    # Descodifica automáticamente el dato pasado en la URL
    result = pytracking.get_open_tracking_result(data)
    
    email_cliente = result.metadata.get("email")
    print(f"Correo abierto por: {email_cliente}")

    # Guardamos fichero con los correos abiertos 
    with open("emails_abiertos.txt", "a") as f:
        f.write(f"{email_cliente}\n")

    # Usamos la función de la librería para devolver el píxel perfecto
    pixel_data, mime_type = pytracking.get_open_tracking_pixel()
    return Response(content=pixel_data, media_type=mime_type)
