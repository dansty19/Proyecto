"""
Imagina que esta API es una biblioteca de películas:
La función load_movies() es como un bibliotecario que carga el catálogo de libros (peliculas) cuando se abre la biblioteca.
La función get_movies() muestra todo el catálogo cuando alguien lo pide.
La función get_movie(id) es como si alguien preguntara por un libro específico por su código de identificación.
La función chatbot (query) es un asistente que busca libros según palabras clave y sinónimo.
La función get_movies_by_category (cagory) ayuda a encontrar películas según su género (acción, comedia, etc.).
"""

# Importamos las herramientas necesarias para contruir nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse para páginas web, JSONResponse para respuestas en formato JSON. 
import pandas as pd # Pandas nos ayuda a manejar datos en tablasm como si fuera un Excel.
import nltk # NLTK es una librería para procesar texto y analizar palabras. 
from nltk.tokenize import word_tokenize # Se usa para dividir un texto en palabras individuales.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinonimos de palabras. 

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador. 
#nltk.data.path.append('C:\Users\Daniel Quintero\AppData\Roaming\nltk_data')

# Descargamos las herramientas necesarias de NLTK para el análisis de palabras.

nltk.download('punkt') # Paquete para dividir frases en palabras.
nltk.download('wordnet') # Paquete para encontrar sinonimos de palabras en inglés.


def imc():
    # Leemos el archivo que contiene información de películas y seleccionamos las columnas más importantes
    df = pd.read_csv("dataset/Hipertension_Arterial_Mexico_MoH-modificado.csv")[['FOLIO_I', 'sexo', 'edad', 'peso', 'estatura', 'masa_corporal', 'riesgo_hipertension']]
    
    # Renombramos las columnas para que sean más faciles de entender
    df.columns = ['Folio', 'Sexo', 'Edad', 'Peso', 'Estatura', 'Masa_Corporal', 'Riesgo_Hipertension']
    
    # Llenamos los espacios vacíos con texto vacío y convertimos los datos en una lista de diccionarios 
    return df.fillna('').to_dict(orient='records')

# Cargamos las películas al iniciar la API para no leer el archivo cada vez que alguien pregunte por ellas.
#movies_list = imc()
imc_list = imc()

#Función para encontrar sinónimos de una palabra
def get_synonyms(word): 
    # Usamos WordNet para obtener distintas palabras que significan lo mismo.
    return{lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}




# Creamos la aplicación FastAPI, que será el motor de nuestra API
# Esto inicializa la API con un nombre y una versión
app = FastAPI(title="Mi aplicación de Salud", version="1.0.0")
# Ruta de inicio: Cuando alguien entra a la API sin especificar nada, verá un mensaje de bienvenida.
@app.get('/', tags=['Home'])
def home():
# Cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida
    return HTMLResponse('<h1>Bienvenido a la API de Salud</h1>')




# Obteniendo la lista de Salud
# Creamos una ruta para obtener todas los datos de salud
# Ruta para obtener todas los datos de salud disponibles
@app.get('/salud', tags=['Salud'])
def get_salud():
    # Si hay películas, las enviamos, si no, mostramos un error
    return imc_list or HTTPException(status_code=500, detail="No hay datos de películas disponibles")


# Ruta para obtener una película específica según su ID
@app.get('/salud/{Peso}', tags=['Salud'])
def get_salud(Peso: str):
    # Buscamos en la lista de películas la que tenga el mismo ID
    return next((m for m in imc_list if m['Peso'] == Peso), {"detalle": "película no encontrada"})

# Ruta del chatbot que responde con películas según palabras clave de la categoría

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave, para entender mejor la intención del usuario
    query_words = word_tokenize(query.lower())
    
    # Buscamos sinónimos de las palabras clave para ampliar la búsqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
    
    # Filtramos la lista de películas buscando coincidencias en la categoría
    results = [m for m in imc_list if any (s in m['Sexo'].lower() for s in synonyms)]
    
    # Si encontramos películas, enviamos la lista; si no, mostramos un mensaje de que no se encontraron coincidencias
    
    return JSONResponse (content={
        "respuesta": "Aquí tienes algunas películas relacionadas." if results else "No encontré películas en esa categoría.",
        "películas": results
    })
    
# Ruta para buscar películas por categoría específica

@app.get ('/salud/by_Sexo/', tags=['Salud'])
def get_movies_by_category(Sexo: str):
    # Filtramos la lista de películas según la categoría ingresada
    return [m for m in imc_list if Sexo.lower() in m['Sexo'].lower()]