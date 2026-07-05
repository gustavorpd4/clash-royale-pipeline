#SCRIPT PARA PRUEBA INICIAL DE API

import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("CLASH_API_TOKEN")
headers = {"Authorization": f"Bearer {TOKEN}"}

url = "https://api.clashroyale.com/v1/cards"
response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Respuesta completa:", response.json())