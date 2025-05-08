import io
from flask import Flask, render_template, request, session
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones
UPLOAD_FOLDER = 'static'

def generar_grafica_lineas(df, x_column, y_column, output_path):
    """
    Función para generar una gráfica a partir de un DataFrame y columnas seleccionadas.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df[x_column], df[y_column], label=f'{y_column} vs {x_column}', color='blue')
    plt.title(f'{y_column} vs {x_column}')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()

def generar_grafica_barras(df, x_column, y_column, output_path):
    """
    Función para generar una gráfica de barras de acuerdo a lista entrega a la funcion como parametro a partir de un DataFrame y columnas seleccionadas.
    """
    plt.figure(figsize=(12, 6))
    df.groupby(x_column)[y_column].sum().plot(kind='bar', color='blue')
    plt.title(f'{y_column} vs {x_column}')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()

    

@app.route('/', methods=['GET', 'POST'])
def upload_and_generate():
    graph_file_lineas = None
    dfhead_html = None
    dfdescribe_html = None
    dfinfo_html = None
    columnas = None

    if request.method == 'POST':
        if 'file' in request.files:  # Carga inicial del archivo
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                try:
                    # Guardar el archivo en el servidor
                    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(file_path)

                    # Leer el archivo CSV
                    df = pd.read_csv(file_path)
                    if df.empty or df.columns.size == 0:
                        return "El archivo CSV no contiene columnas. Por favor, suba un archivo válido.", 400

                    # Guardar la ruta del archivo en la sesión
                    session['file_path'] = file_path

                    # Generar vista previa, descripción y columnas
                    dfhead_html = df.head().to_html(classes='table table-striped', index=False)
                    dfdescribe_html = df.describe(include='all').to_html(classes='table table-striped', index=False)

                    buffer = io.StringIO()
                    df.info(buf=buffer)
                    dfinfo_html = f"<pre>{buffer.getvalue()}</pre>"

                    columnas = df.columns.tolist()

                except Exception as e:
                    return f"Error al procesar el archivo: {str(e)}", 400
            else:
                return "Por favor suba un archivo CSV válido.", 400

        elif 'x_column' in request.form and 'y_column' in request.form:  # Generar gráfica
            try:
                # Recuperar el archivo CSV desde la sesión
                file_path = session.get('file_path')
                if not file_path or not os.path.exists(file_path):
                    return "El archivo CSV no está disponible. Por favor, cargue un archivo nuevamente.", 400

                # Leer el archivo CSV
                df = pd.read_csv(file_path)

                # Obtener las columnas seleccionadas
                x_column = request.form['x_column']
                y_column = request.form['y_column']

                # Crear la gráfica utilizando la función separada
                graph_file_lineas = os.path.join(UPLOAD_FOLDER, 'grafico_lineas.png')
                generar_grafica_lineas(df, x_column, y_column, graph_file_lineas)

                # Mantener las columnas disponibles para el formulario
                columnas = df.columns.tolist()

                # Mantener los datos para los bloques if dfhead, if dfinfo, if dfdescribe
                dfhead_html = df.head().to_html(classes='table table-striped', index=False)
                dfdescribe_html = df.describe(include='all').to_html(classes='table table-striped', index=False)

                buffer = io.StringIO()
                df.info(buf=buffer)
                dfinfo_html = f"<pre>{buffer.getvalue()}</pre>"

            except Exception as e:
                return f"Error al generar la gráfica: {str(e)}", 400

    return render_template(
        'myapp.html',
        graph_file_lineas=graph_file_lineas,
        dfhead=dfhead_html,
        dfdescribe=dfdescribe_html,
        dfinfo=dfinfo_html,
        columnas=columnas
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
