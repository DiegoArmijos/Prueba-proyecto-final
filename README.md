# Calculadora de Huella de Carbono y Reciclaje

Aplicación web en Flask para calcular la huella de carbono personal y evaluar hábitos de reciclaje.

## Descripción

Esta aplicación permite a los usuarios:
- Calcular emisiones de CO₂ a partir de transporte, energía y uso de plástico.
- Clasificar el resultado en niveles `BAJO`, `MEDIO` o `ALTO`.
- Guardar un historial de mediciones.
- Evaluar acciones de reciclaje y el CO₂ evitado.
- Consultar un historial de puntajes de reciclaje.

## Tecnologías

- Python 3
- Flask
- Jinja2
- HTML/CSS

## Instalación

1. Clona el repositorio:

```bash
git clone <URL-del-repositorio>
cd "Proyecto final"
```

2. Crea y activa un entorno virtual:

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows CMD:
```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación con:

```bash
python main.py
```

Luego abre `http://127.0.0.1:5000/` en tu navegador.

## Estructura del proyecto

- `main.py` - Lógica principal de Flask y cálculos.
- `requirements.txt` - Dependencias del proyecto.
- `static/` - Archivos estáticos como CSS.
- `templates/` - Plantillas HTML de Flask.
- `datos_co2.json` - Historial de cálculos de carbono (generado automáticamente).
- `datos_recicla.json` - Historial de reciclaje (generado automáticamente).

## Notas

- No es necesario subir los archivos generados `datos_co2.json` y `datos_recicla.json` al repositorio.
- Si deseas usar este proyecto en un servidor de producción, configura un servidor WSGI como Gunicorn.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta `LICENSE` para más detalles.
