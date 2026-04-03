from flask import Flask, render_template, request
import json
import os

print("RUTA ACTUAL:", os.getcwd())

app = Flask(__name__)

def guardar_datos(datos):
    try:
        with open("datos.json", "r") as f:
            contenido = json.load(f)
    except Exception:
        contenido = []

    contenido.append(datos)

    with open("datos.json", "w") as f:
        json.dump(contenido, f)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/calcular", methods=["POST"])
def calcular():

    # 🌍 Transporte
    transporte_tipo = request.form["transporte"]
    horas_transporte = int(request.form["horas_transporte"])

    # ⚡ Otros datos
    energia = int(request.form["energia"])
    plastico = int(request.form["plastico"])

    # 🔥 Ajuste transporte
    horas = horas_transporte // 2

    if horas > 5:
        horas = 5

    if transporte_tipo == "carro":
        transporte = horas * 3
    elif transporte_tipo == "bus":
        transporte = horas * 2
    elif transporte_tipo == "bici":
        transporte = horas * 1
    else:
        transporte = 0

    # ⚡ Energía balanceada
    energia_puntos = energia // 2
    if energia_puntos > 4:
        energia_puntos = 4

    # 🧮 TOTAL
    puntos = transporte + energia_puntos + plastico

    # 📊 NIVEL
    if puntos <= 8:
        nivel = "BAJO 🌱"
    elif puntos <= 13:
        nivel = "MEDIO ⚠️"
    else:
        nivel = "ALTO 🚨"

    # 🎨 COLOR BARRA
    if puntos <= 7:
        color = "green"
    elif puntos <= 13:
        color = "yellow"
    else:
        color = "red"

    # 💾 GUARDAR
    datos = {
        "puntos": puntos,
        "nivel": nivel
    }

    guardar_datos(datos)

    # 💡 RECOMENDACIONES
    recomendaciones = []

    # --- por nivel ---
    if nivel.startswith("BAJO"):
        recomendaciones.append("🌱 ¡Excelente! Mantén tus hábitos sostenibles.")
        recomendaciones.append("♻️ Inspira a otros a cuidar el planeta.")

    elif nivel.startswith("MEDIO"):
        recomendaciones.append("⚠️ Vas bien, pero puedes mejorar algunos hábitos.")
        recomendaciones.append("🚲 Usa más transporte sostenible cuando puedas.")

    elif nivel.startswith("ALTO"):
        recomendaciones.append("🚨 Tu impacto ambiental es alto.")
        recomendaciones.append("🌍 Es urgente reducir consumo y transporte contaminante.")

    # --- por acciones ---
    if transporte_tipo == "carro" and horas_transporte >= 4:
        recomendaciones.append("🚗 Usas bastante el carro, intenta reducirlo o compartir viajes.")

    if energia > 6:
        recomendaciones.append("⚡ Reduce el uso de electricidad en casa.")

    if plastico > 3:
        recomendaciones.append("🧴 Disminuye el uso de plásticos desechables.")

    # si todo está bien
    if not recomendaciones:
        recomendaciones.append("🎉 ¡Excelente! Tienes hábitos sostenibles.")

    return render_template(
        "resultado.html",
        puntos=puntos,
        nivel=nivel,
        color=color,
        recomendaciones=recomendaciones
    )


@app.route("/historial")
def historial():
    try:
        with open("datos.json", "r") as f:
            datos = json.load(f)
    except Exception:
        datos = []

    return render_template("historial.html", datos=datos)


if __name__ == "__main__":
    app.run(debug=True)