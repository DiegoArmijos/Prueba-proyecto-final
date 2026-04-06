from flask import Flask, render_template, request
from datetime import datetime
import json, os

app = Flask(__name__)
CO2_FILE     = "datos_co2.json"
RECICLA_FILE = "datos_recicla.json"

# ── Factores CO₂ ────────────────────────────────────────────────
FACTORES_TRANSPORTE = {"carro":2.4,"bus":0.6,"moto":1.2,"bici":0.0,"pie":0.0}
FACTOR_ENERGIA  = 0.5
FACTOR_PLASTICO = 0.08

# ── Pesos reciclaje (puntos por unidad, cap ×5) ──────────────────
PESOS = {
    "papel":3.0,"plastico_r":4.0,"vidrio":5.0,"metal":4.5,
    "organico":3.5,"reutiliza":10.0,"repara":15.0,
    "rechazo":8.0,"dona":12.0,"compra_usad":6.0,
}
CO2_EVITADO = {
    "papel":0.003,"plastico_r":0.06,"vidrio":0.10,"metal":0.05,
    "organico":0.02,"reutiliza":0.15,"repara":2.50,
    "rechazo":0.12,"dona":1.80,"compra_usad":0.90,
}

# ── Persistencia ─────────────────────────────────────────────────
def _leer(path):
    if not os.path.exists(path): return []
    try:
        c = open(path,"r",encoding="utf-8").read().strip()
        return json.loads(c) if c else []
    except Exception: return []

def _guardar(path, nuevo):
    datos = _leer(path); datos.append(nuevo)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

def estadisticas(datos, campo="co2_total"):
    if not datos: return None
    vals = [d[campo] for d in datos]
    return {"promedio":round(sum(vals)/len(vals),2),"minimo":round(min(vals),2),
            "maximo":round(max(vals),2),"registros":len(datos),
            "tendencia":("mejora" if len(vals)>=2 and vals[-1]<vals[-2] else
                         "empeora" if len(vals)>=2 and vals[-1]>vals[-2] else "igual")}

# ── Helpers CO₂ ──────────────────────────────────────────────────
def clasificar_co2(co2):
    if co2<5:  return "BAJO","green","🌱"
    if co2<12: return "MEDIO","yellow","⚠️"
    return "ALTO","red","🚨"

def equiv_co2(co2):
    return {"arboles":round(co2/0.02,1),"km_auto":round(co2/0.12,1),"cargas":int(round(co2/0.005,0))}

def tips_co2(transporte, horas, energia, plastico, nivel):
    t = []
    if nivel=="BAJO":  t+=[ ("🌱","¡Huella ejemplar!","Tus hábitos son sostenibles. Mantén este ritmo."),("🌍","Inspira a otros","Comparte tus hábitos verdes con amigos y familia.")]
    elif nivel=="MEDIO": t+=[ ("⚠️","Buen camino","Vas bien, pero hay margen de mejora."),("🚲","Transporte verde","Prefiere bicicleta o caminar cuando sea posible.")]
    else: t+=[ ("🚨","Impacto alto","Pequeños cambios diarios tienen gran efecto acumulado."),("🌍","Actúa hoy","Intenta reducir al menos una fuente de emisión mañana.")]
    if transporte=="carro" and horas>=2: t.append(("🚗","Carpooling","Compartir el auto reduce emisiones a la mitad."))
    if transporte in ("carro","moto") and horas>=1: t.append(("🚌","Transporte público","El bus emite hasta 4× menos CO₂ que el carro."))
    if energia>8: t.append(("⚡","Ahorro eléctrico","Usa modo ahorro y apaga dispositivos en standby."))
    if plastico>3: t.append(("🧴","Reduce plástico","Lleva tu propio vaso y bolsa reutilizable."))
    return t[:5]

# ── Helpers Reciclaje ─────────────────────────────────────────────
def calcular_puntos(form):
    puntos=0.0; co2e=0.0; detalle={}
    for campo, peso in PESOS.items():
        v = float(form.get(campo,0) or 0)
        pts = min(v*peso, peso*5)
        puntos += pts; co2e += v*CO2_EVITADO.get(campo,0)
        detalle[campo] = {"val":v,"pts":round(pts,1),"co2e":round(v*CO2_EVITADO.get(campo,0),3)}
    return min(round(puntos,1),100), round(co2e,3), detalle

def clasificar_recicla(p):
    if p>=60: return "HÉROE","green","🏆"
    if p>=30: return "ACTIVO","yellow","♻️"
    return "INICIANDO","red","🌱"

def tips_recicla(det, nivel):
    t = []
    if nivel=="HÉROE": t+=[ ("🏆","¡Eres un referente!","Tu nivel de reciclaje es excepcional. Sigue inspirando."),("📣","Difunde el hábito","Enseña a alguien más a separar sus residuos hoy.")]
    elif nivel=="ACTIVO": t+=[ ("♻️","Vas muy bien","Ya tienes hábitos sólidos. El siguiente nivel está cerca."),("📦","Más Reducción","Antes de reciclar, intenta rechazar o reducir el consumo.")]
    else: t+=[ ("🌱","¡Empieza hoy!","Separar papel y plástico es el primer gran paso."),("🗑️","Tres canecas","Una para orgánicos, una para reciclables y una general.")]
    if det["repara"]["val"]==0: t.append(("🔧","Repara antes de botar","Reparar un objeto evita hasta 2.5 kg de CO₂."))
    if det["rechazo"]["val"]==0: t.append(("🙅","Di no al desechable","Lleva tu botella y bolsa. Cada rechazo cuenta."))
    if det["organico"]["val"]==0: t.append(("🌿","Compostaje","Los residuos orgánicos generan metano. Compóstalos."))
    if det["dona"]["val"]==0: t.append(("👕","Dona lo que no usas","Extender la vida útil de prendas reduce la huella textil."))
    return t[:5]

def calcular_rango(puntos):
    if puntos < 10:
        return "🌱 Novato ecológico"
    elif puntos < 25:
        return "♻️ Consciente"
    elif puntos < 50:
        return "🌍 Guardián del planeta"
    else:
        return "💚 Eco Master"

# ── Rutas ─────────────────────────────────────────────────────────
@app.route("/")
def inicio(): return render_template("inicio.html")

@app.route("/carbono")
def carbono(): return render_template("index.html")

@app.route("/calcular", methods=["POST"])
def calcular():
    tr = request.form.get("transporte","carro")
    h  = max(0,min(float(request.form.get("horas_transporte",0)),12))
    e  = max(0,min(float(request.form.get("energia",0)),24))
    p  = max(0,min(float(request.form.get("plastico",0)),20))
    co2_t=FACTORES_TRANSPORTE.get(tr,0)*h; co2_e=FACTOR_ENERGIA*e; co2_p=FACTOR_PLASTICO*p
    co2=round(co2_t+co2_e+co2_p,2)
    nivel,color,emoji=clasificar_co2(co2)
    _guardar(CO2_FILE,{"fecha":datetime.now().strftime("%d/%m/%Y %H:%M"),
        "co2_total":co2,"co2_transporte":round(co2_t,2),"co2_energia":round(co2_e,2),
        "co2_plastico":round(co2_p,2),"nivel":nivel,"transporte":tr})
    return render_template("resultado.html",co2=co2,co2_t=round(co2_t,2),co2_e=round(co2_e,2),
        co2_p=round(co2_p,2),nivel=nivel,emoji=emoji,color=color,
        porcentaje=min(round((co2/20)*100),100),
        pct_t=min(round(co2_t/20*100),100),pct_e=min(round(co2_e/20*100),100),
        pct_p=min(round(co2_p/20*100),100),
        recomendaciones=tips_co2(tr,h,e,p,nivel),equiv=equiv_co2(co2))

@app.route("/historial")
def historial():
    d=_leer(CO2_FILE); return render_template("historial.html",datos=d,stats=estadisticas(d))

@app.route("/recicla")
def recicla(): return render_template("recicla.html")

@app.route("/calcular-recicla", methods=["POST"])
def calcular_recicla():
    puntos,co2e,det=calcular_puntos(request.form)
    nivel,color,emoji=clasificar_recicla(puntos)
    _guardar(RECICLA_FILE,{"fecha":datetime.now().strftime("%d/%m/%Y %H:%M"),
        "puntos":puntos,"co2_evitado":co2e,"nivel":nivel})
    return render_template("resultado_recicla.html",puntos=puntos,co2_evitado=co2e,
        detalle=det,nivel=nivel,emoji=emoji,color=color,porcentaje=min(round(puntos),100),
        recomendaciones=tips_recicla(det,nivel),
        arboles=round(co2e/0.02,1),bolsas=int(co2e/0.008))

@app.route("/historial-recicla")
def historial_recicla():
    d=_leer(RECICLA_FILE)
    return render_template("historial_recicla.html",datos=d,stats=estadisticas(d,"puntos"))

@app.route("/wordle")
def wordle():
    return render_template("wordle.html")

if __name__ == "__main__":
    app.run(debug=True)