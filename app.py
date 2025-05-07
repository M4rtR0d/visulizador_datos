import io
from flask import Flask, render_template, request, session
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = '123'  # Necesario para usar sesiones
UPLOAD_FOLDER = 'static'

''' 
def crear_grafica(df, filename='grafico.png'):

    # Obtener las columnas seleccionadas del formulario
    x_column = request.form['x_column']
    y_column = request.form['y_column']

    # Crear un gráfico de líneas para el precio de cierre
    plt.figure(figsize=(12, 6))
    plt.plot(df['x_column'], df['y_column'], label=f'{y_column} vs {x_column}', color='blue')
    plt.title(f'Gráfica de {y_column} vs {x_column}')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.legend()
    plt.grid(True)
    
    # Guardar la figura
    graph_path = os.path.join(UPLOAD_FOLDER, filename)
    plt.savefig(graph_path)
    plt.close()
'''
@app.route('/crear_grafica', methods=['POST'])
def crear_grafica():
    try:
        # Obtener las columnas seleccionadas del formulario
        x_column = request.form['x_column']
        y_column = request.form['y_column']

        # Recuperar el archivo CSV desde la sesión
        file_path = session.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return "El archivo CSV no está disponible. Por favor, cargue un archivo nuevamente.", 400

        # Leer el archivo CSV
        df = pd.read_csv(file_path, parse_dates=['Fecha'], low_memory=False)

        # Crear la gráfica con las columnas seleccionadas
        plt.figure(figsize=(12, 6))
        plt.plot(df[x_column], df[y_column], label=f'{y_column} vs {x_column}', color='blue')
        plt.title(f'Gráfica de {y_column} vs {x_column}')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.legend()
        plt.grid(True)

        # Guardar la figura
        graph_path = os.path.join(UPLOAD_FOLDER, 'grafico_personalizado.png')
        plt.savefig(graph_path)
        plt.close()

        # Renderizar la plantilla con la nueva gráfica
        return render_template('myapp.html', graph_file=graph_path, columnas=df.columns.tolist())

    except Exception as e:
        return f"Error al generar la gráfica: {str(e)}", 400
     
@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        # Verificar si se subió un archivo
        if 'file' not in request.files:
            return "No se encontró el archivo. Por favor, suba un archivo CSV.", 400

        file = request.files['file']

        # Verificar si el archivo es un CSV
        if file and file.filename.endswith('.csv'):
            try:
                # Guardar el archivo en el servidor
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)

                # Leer el archivo CSV
                try:
                    df = pd.read_csv(file_path, parse_dates=['Fecha'], low_memory=False)
                except pd.errors.EmptyDataError:
                    return "El archivo CSV está vacío. Por favor, suba un archivo válido.", 400
                except pd.errors.ParserError:
                    return "El archivo no tiene un formato CSV válido. Por favor, suba un archivo válido.", 400

                # Validar que el archivo tenga columnas
                if df.empty or df.columns.size == 0:
                    return "El archivo CSV no contiene columnas. Por favor, suba un archivo válido.", 400

                # Guardar la ruta del archivo en la sesión
                session['file_path'] = file_path

                # Generar vista previa, descripción y columnas
                dfhead = df.head()
                dfhead_html = dfhead.to_html(classes='table table-striped', index=False)

                dfdescribe = df.describe(include='all')
                dfdescribre_html = dfdescribe.to_html(classes='table table-striped', index=False)

                buffer = io.StringIO()
                df.info(buf=buffer)
                dfinfo = buffer.getvalue()
                dfinfo_html = f"<pre>{dfinfo}</pre>"

                columnas = df.columns.tolist()

                # Renderizar la plantilla con las variables necesarias
                return render_template(
                    'myapp.html',
                    graph_file=None,
                    dfhead=dfhead_html,
                    dfdescribe=dfdescribre_html,
                    dfinfo=dfinfo_html,
                    columnas=columnas
                )
            except Exception as e:
                return f"Error al procesar el archivo: {str(e)}", 400
        else:
            return "Por favor suba un archivo CSV válido.", 400

    return render_template('myapp.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
