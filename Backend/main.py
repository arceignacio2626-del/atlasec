from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import scanner

app = FastAPI(title="Atlasec API", description="API de escaneo de seguridad para PYMEs")

# CORS - Permite que tu frontend en Vercel se comunique con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia esto por tu dominio de Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)

class SolicitudEscaneo(BaseModel):
    url: str

@app.post("/escanear")
def escanear_sitio(solicitud: SolicitudEscaneo):
    url = solicitud.url
    
    # Ejecutar el escáner
    resultados = scanner.escanear_seguridad(url)
    
    # Si hay error, devolverlo
    if "error" in resultados:
        return {
            "success": False,
            "error": resultados["error"]
        }
    
    # Generar reporte en texto plano (esto luego lo mejorará la IA)
    reporte = generar_reporte_texto(resultados)
    
    return {
        "success": True,
        "url": resultados["url"],
        "resultados": resultados,
        "reporte": reporte
    }

def generar_reporte_texto(resultados):
    """Genera un reporte básico en texto"""
    reporte = f" REPORTE DE SEGURIDAD - {resultados['url']}\n\n"
    
    # HTTPS
    if resultados["https"]:
        reporte += "✅ HTTPS: Tu sitio usa conexión segura\n"
    else:
        reporte += "❌ HTTPS: Tu sitio NO usa HTTPS (riesgo alto)\n"
    
    # Headers
    headers = resultados["headers"]
    if headers["x_frame_options"]:
        reporte += "✅ Protección Clickjacking: Activada\n"
    else:
        reporte += "⚠️ Protección Clickjacking: Desactivada\n"
    
    if headers["x_content_type_options"]:
        reporte += "✅ Protección MIME Sniffing: Activada\n"
    else:
        reporte += "⚠️ Protección MIME Sniffing: Desactivada\n"
    
    # Archivos expuestos
    if resultados["archivos_expuestos"]:
        reporte += f"\n️ Archivos expuestos detectados: {', '.join(resultados['archivos_expuestos'])}\n"
    else:
        reporte += "\n✅ No se detectaron archivos sensibles expuestos\n"
    
    return reporte

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a Atlasec API - Tu escáner de seguridad está activo"}