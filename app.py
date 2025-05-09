import io
from flask import Flask, render_template, request, session
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones
UPLOAD_FOLDER = 'static'

def generar_grafica_lineas(df, x_column, y_column, output_path):
    """
    Función para generar una gráfica a partir de un DataFrame y columnas seleccionadas.
    """
    if not x_column and y_column:
        raise ValueError("No se seleccionaron columnas para generar el gráfico de barras.")

    plt.figure(figsize=(12, 6))
    plt.plot(df[x_column], df[y_column], label=f'{y_column} vs {x_column}', color='blue')
    plt.title(f'{y_column} vs {x_column}')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    # Ajustar la frecuencia de los xticks
    # Mostrar un xtick cada 10 valores o más, según el tamaño del DataFrame
    xtick_frequency = max(len(df[x_column]) // 10, 1)  
    # Seleccionar etiquetas con la frecuencia ajustada
    plt.xticks(df[x_column][::xtick_frequency], rotation=45)  
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()

def generar_grafica_multiple(df, selected_columns, output_path):
    """
    Función para generar una gráfica con múltiples columnas seleccionadas.
    """
    if not selected_columns:
        raise ValueError("No se seleccionaron columnas para generar el gráfico de barras.")

    plt.figure(figsize=(12, 6))
    for column in selected_columns:
        plt.plot(df.index, df[column], label=column)
    plt.title("Gráfico de columnas seleccionadas")
    plt.xlabel("Índice")
    plt.ylabel("Valores")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()

def generar_grafica_barras(df, selected_columns, output_path):
    """
    Función para generar un gráfico de barras con múltiples columnas seleccionadas.
    """
    if not selected_columns:
        raise ValueError("No se seleccionaron columnas para generar el gráfico de barras.")

    # Validar que todas las columnas existan en el DataFrame
    for column in selected_columns:
        if column not in df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame.")

    plt.figure(figsize=(12, 6))
    bar_width = 0.8 / len(selected_columns)  # Ajustar el ancho de las barras para múltiples columnas
    indices = range(len(df.index))

    for i, column in enumerate(selected_columns):
        plt.bar(
            [x + i * bar_width for x in indices],  # Desplazar las barras para cada columna
            df[column],
            bar_width,
            label=column
        )

    plt.title("Gráfico de barras de columnas seleccionadas")
    plt.xlabel("Índice")
    plt.ylabel("Valores")
    plt.xticks([x + bar_width * (len(selected_columns) / 2 - 0.5) for x in indices], df.index, rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(output_path)  # Guardar el gráfico en el archivo especificado
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def upload_and_generate():
    # Recuperar las rutas de los gráficos desde la sesión
    graph_file_lineas = session.get('graph_file_lineas', None)
    graph_file_multiple = session.get('graph_file_multiple', None)
    graph_file_barras = session.get('graph_file_barras', None)
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

        elif 'x_column' in request.form and 'y_column' in request.form:  # Generar gráfica de líneas
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

                # Guardar la ruta del gráfico en la sesión
                session['graph_file_lineas'] = graph_file_lineas

                # Mantener las columnas disponibles para el formulario
                columnas = df.columns.tolist()
                # Mantener los datos para los bloques if dfhead, if dfinfo, if dfdescribe
                dfhead_html = df.head().to_html(classes='table table-striped', index=False)
                dfdescribe_html = df.describe(include='all').to_html(classes='table table-striped', index=False)

                buffer = io.StringIO()
                df.info(buf=buffer)
                dfinfo_html = f"<pre>{buffer.getvalue()}</pre>"

            except Exception as e:
                return f"Error al generar la gráfica de líneas: {str(e)}", 400

        elif 'selected_columns_multiple' in request.form:  # Generar gráfica múltiple
            try:
                # Recuperar el archivo CSV desde la sesión
                file_path = session.get('file_path')
                if not file_path or not os.path.exists(file_path):
                    return "El archivo CSV no está disponible. Por favor, cargue un archivo nuevamente.", 400

                # Leer el archivo CSV
                df = pd.read_csv(file_path)

                # Obtener las columnas seleccionadas
                selected_columns_multiple = request.form.getlist('selected_columns_multiple')

                # Crear la gráfica utilizando la función separada
                graph_file_multiple = os.path.join(UPLOAD_FOLDER, 'grafico_multiple.png')
                generar_grafica_multiple(df, selected_columns_multiple, graph_file_multiple)

                # Guardar la ruta del gráfico en la sesión
                session['graph_file_multiple'] = graph_file_multiple

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
            
        elif 'selected_columns' in request.form:  # Generar gráfica de barras
            try:
                # Recuperar el archivo CSV desde la sesión
                file_path = session.get('file_path')
                if not file_path or not os.path.exists(file_path):
                    return "El archivo CSV no está disponible. Por favor, cargue un archivo nuevamente.", 400

                # Leer el archivo CSV
                df = pd.read_csv(file_path)

                # Obtener las columnas seleccionadas
                selected_columns = request.form.getlist('selected_columns')
                if not selected_columns:
                    return "No se seleccionaron columnas para generar el gráfico de barras.", 400

                # Crear la gráfica utilizando la función separada
                graph_file_barras = os.path.join(UPLOAD_FOLDER, 'grafico_barras.png')
                generar_grafica_barras(df, selected_columns, graph_file_barras)

                # Guardar la ruta del gráfico en la sesión
                session['graph_file_barras'] = graph_file_barras

                # Mantener las columnas disponibles para el formulario
                columnas = df.columns.tolist()

                # Mantener los datos para los bloques if dfhead, if dfinfo, if dfdescribe
                dfhead_html = df.head().to_html(classes='table table-striped', index=False)
                dfdescribe_html = df.describe(include='all').to_html(classes='table table-striped', index=False)

                buffer = io.StringIO()
                df.info(buf=buffer)
                dfinfo_html = f"<pre>{buffer.getvalue()}</pre>"

            except Exception as e:
                return f"Error al generar la gráfica de barras: {str(e)}", 400

    return render_template(
        'myapp.html',
        graph_file_lineas=graph_file_lineas,
        graph_file_multiple=graph_file_multiple,
        graph_file_barras=graph_file_barras,
        dfhead=dfhead_html,
        dfdescribe=dfdescribe_html,
        dfinfo=dfinfo_html,
        columnas=columnas
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
