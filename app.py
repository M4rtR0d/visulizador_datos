import io
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static'

def crear_grafica(df, filename='grafico.png'):
    # Crear un gráfico de líneas para el precio de cierre
    plt.figure(figsize=(12, 6))
    plt.plot(df['Fecha'], df['Valor hoy'], label='Cierre', color='blue')
    plt.title('Indice MSCI COLCAP')
    plt.xlabel('Fecha')
    plt.ylabel('Indice')
    plt.legend()
    plt.grid(True)
    
    # Guardar la figura
    graph_path = os.path.join(UPLOAD_FOLDER, filename)
    plt.savefig(graph_path)
    plt.close()


@app.route('/', methods=['GET', 'POST'])
# Crear funcion para subir archivo, verificar extension .csv y convertirlo a dataframe
def upload_csv():
    if request.method == 'POST':
        # Verificar si se subió un archivo
        file = request.files['file']

        # Verificar si el archivo es un CSV
        if file and file.filename.endswith('.csv'):
            try:
                # Leer el archivo CSV
                df = pd.read_csv(file, parse_dates=['Fecha'], low_memory=False)

                dfhead=df.head()
                # Convierte dfhead a HTML para pasarlo a la plantilla
                dfhead_html = dfhead.to_html(classes='table table-striped', index=False)

                dfdescribe = df.describe(include='all')
                dfdescribre_html = dfdescribe.to_html(classes='table table-striped', index=False)

                # Captura la salida de df.info() en un buffer de texto
                buffer = io.StringIO()
                df.info(buf=buffer)
                dfinfo = buffer.getvalue()  # Obtén el contenido del buffer como una cadena
                dfinfo_html = f"<pre>{dfinfo}</pre>"  # Formatea como HTML preformateado

                crear_grafica(df)


                # retorna en myapp.html el grafico del dataframe
                return render_template('myapp.html', graph_file='grafico.png', dfhead=dfhead_html, dfdescribe=dfdescribre_html, dfinfo=dfinfo_html)   
            
            except Exception as e:
                return f"Error al procesar el archivo: {str(e)}", 400
        else:
            return "Por favor suba un archivo csv valido", 400
        
    return render_template('myapp.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
