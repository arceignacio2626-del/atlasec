import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generar_reporte_ia(resultados_escaneo):
    # Usar el modelo actual (2024-2025)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """Eres "Atlas", experto en ciberseguridad de Atlasec.
Explica estos resultados a dueños de PYMEs en español, sin tecnicismos.

Estructura obligatoria:
- 🛡️ **Resumen Ejecutivo**: 2-3 frases del estado general
- 🔴 **Riesgos Detectados**: qué significa cada problema en dinero/reputación/leyes
- 🟢 **Plan de Acción**: 3 pasos claros para solucionarlo

Resultados del escaneo:
""" + resultados_escaneo

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error con IA: {e}"