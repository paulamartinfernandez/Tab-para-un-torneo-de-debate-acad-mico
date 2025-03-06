from flask import Flask, render_template, request, redirect, url_for, send_file
from functions import Miembro, Equipo, registrar_equipo, enfrentamientos_iniciales, enfrentamientos_clasificatoria, resultados_ronda, fases_finales
import csv 

app = Flask(__name__)

# Lista global para almacenar los equipos
equipos = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registrar_equipos", methods=["GET", "POST"])
def registrar_equipos():
    if request.method == "POST":
        nombre_equipo = request.form.get("nombre_equipo")
        miembros = []

        # Recuperar los miembros del formulario
        for i in range(5):
            nombre = request.form.get(f"miembros[{i}][nombre]")
            puntos_orador = request.form.get(f"miembros[{i}][puntos_orador]", type=int)

            # Solo agregar si hay un nombre de miembro
            if nombre:
                miembros.append({'nombre': nombre, 'puntos_orador': puntos_orador})

        victorias = request.form.get("victorias", type=int)
        items = request.form.get("items", type=int)

        try:
            registrar_equipo(equipos, nombre_equipo, miembros, victorias, items)
            return redirect(url_for("index"))
        except ValueError as e:
            return str(e), 400  # Devuelve un mensaje de error si la validación falla

    return render_template("registrar_equipos.html")


@app.route("/clasificacion_equipos")
@app.route("/clasificacion_equipos")
def clasificacion_equipos():
    # Ordenar los equipos primero por victorias y luego por puntos
    equipos_ordenados = sorted(equipos, key=lambda equipo: (equipo.victorias, equipo.items), reverse=True)
    return render_template("clasificacion_equipos.html", equipos=equipos_ordenados)

@app.route("/clasificacion_oradores")
def clasificacion_oradores():
    oradores = []
    for equipo in equipos:
        for miembro in equipo.miembros:
            oradores.append((miembro.nombre, miembro.puntos_orador, equipo.nombre))
    oradores_ordenados = sorted(oradores, key=lambda x: x[1], reverse=True)
    return render_template("clasificacion_oradores.html", oradores=oradores_ordenados)

@app.route("/enfrentamientos", methods=["GET", "POST"])
def enfrentamientos():
    if request.method == "POST":
        fase = request.form.get("fase")
        if fase == "inicial":
            enfrentamientos = enfrentamientos_iniciales(equipos)
        elif fase == "clasificatoria":
            enfrentamientos = enfrentamientos_clasificatoria(equipos)
        elif fase in ["octavos", "cuartos", "semifinales", "final"]:
            equipos_clasifican, enfrentamientos = fases_finales(equipos, fase)
        else:
            return "Fase no válida", 400

        return render_template("enfrentamientos.html", enfrentamientos=enfrentamientos)

    return render_template("enfrentamientos.html")

@app.route("/registrar_resultados", methods=["GET", "POST"])
def registrar_resultados():
    if request.method == "POST":
        resultados = {}  # Para almacenar las victorias de cada equipo
        items_de_equipo = {}  # Para almacenar los ítems de cada equipo
        puntos_orador = {}  # Para almacenar los puntos de cada orador

        # Procesar los datos del formulario
        for key, value in request.form.items():
            if key.startswith("ganador_"):
                # Registrar el ganador
                equipo_ganador = value
                resultados[equipo_ganador] = resultados.get(equipo_ganador, 0) + 1
            elif key.startswith("items_"):
                # Registrar los ítems de cada equipo
                equipo = key.split("_")[1]
                items_de_equipo[equipo] = int(value)
            elif key.startswith("puntos_"):
                # Registrar los puntos de cada orador
                orador = key.split("_")[1]
                puntos_orador[orador] = int(value)

        # Actualizar las estadísticas de los equipos y oradores
        resultados_ronda(equipos, resultados, items_de_equipo, puntos_orador)
        return redirect(url_for("index"))

    # Si es una solicitud GET, generar los enfrentamientos y mostrarlos
    enfrentamientos_generados = enfrentamientos_iniciales(equipos)  # Generar enfrentamientos
    return render_template("registrar_resultados.html", enfrentamientos=enfrentamientos_generados, equipos=equipos)

    # # Si es una solicitud GET, generar los enfrentamientos y mostrarlos
    # enfrentamientos_generados = enfrentamientos_iniciales(equipos)  # Generar enfrentamientos
    # return render_template("registrar_resultados.html", enfrentamientos=enfrentamientos_generados)
@app.route("/exportar_clasificacion_equipos")
def exportar_clasificacion_equipos():
    # Ordenar los equipos primero por victorias y luego por puntos
    equipos_ordenados = sorted(equipos, key=lambda equipo: (equipo.victorias, equipo.items), reverse=True)
    
    # Definir el nombre del archivo CSV
    archivo_csv = "clasificacion_equipos.csv"

    # Abrir el archivo en modo escritura
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nombre del Equipo', 'Victorias', 'Ítems', 'Miembro', 'Puntos'])  # Encabezados

        # Escribir los datos de cada equipo
        for equipo in equipos_ordenados:
            for miembro in equipo.miembros:
                writer.writerow([equipo.nombre, equipo.victorias, equipo.items, miembro.nombre, miembro.puntos_orador])

    return send_file(archivo_csv, as_attachment=True)

@app.route("/exportar_clasificacion_oradores")
def exportar_clasificacion_oradores():
    oradores = []
    for equipo in equipos:
        for miembro in equipo.miembros:
            oradores.append((miembro.nombre, miembro.puntos_orador, equipo.nombre))
    
    oradores_ordenados = sorted(oradores, key=lambda x: x[1], reverse=True)
    
    # Definir el nombre del archivo CSV
    archivo_csv = "clasificacion_oradores.csv"

    # Abrir el archivo en modo escritura
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nombre Orador', 'Puntos', 'Equipo'])  # Encabezados

        # Escribir los datos de cada orador
        for orador, puntos, equipo in oradores_ordenados:
            writer.writerow([orador, puntos, equipo])

    return send_file(archivo_csv, as_attachment=True)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)