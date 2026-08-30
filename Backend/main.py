from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import scanner

app = FastAPI(title="Atlasec API", description="API de escaneo de seguridad para PYMEs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SolicitudEscaneo(BaseModel):
    url: str

@app.post("/escanear")
def escanear_sitio(solicitud: SolicitudEscaneo):
    url = solicitud.url
    resultados = scanner.escanear_seguridad(url)
    
    if "error" in resultados:
        return {"success": False, "error": resultados["error"]}
    
    reporte = generar_reporte(resultados)
    
    return {
        "success": True,
        "url": resultados["url"],
        "score": resultados["score"],
        "nivel_riesgo": resultados["nivel_riesgo"],
        "resultados": resultados,
        "reporte": reporte
    }

def generar_reporte(r):
    """Genera reporte completo"""
    lines = []
    lines.append(f"REPORTE DE SEGURIDAD - {r['url']}")
    lines.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append(f"Score de Seguridad: {r['score']}/100")
    lines.append(f"Nivel de Riesgo: {r['nivel_riesgo']}")
    lines.append("=" * 50)
    lines.append("")
    
    # HTTPS
    lines.append("🔒 CONEXIÓN SEGURA")
    if r["https"]:
        lines.append("  ✅ Sitio usa HTTPS")
    else:
        lines.append("  ❌ Sitio NO usa HTTPS (RIESGO ALTO)")
    
    if r.get("ssl", {}).get("valido"):
        ssl_info = r["ssl"]
        lines.append(f"  ✅ Certificado SSL válido")
        lines.append(f"  📅 Expira: {ssl_info['expira']} ({ssl_info['dias_restantes']} días)")
        lines.append(f"  🏢 Emisor: {ssl_info['emisor']}")
    lines.append("")
    
    # Headers
    lines.append("️ HEADERS DE SEGURIDAD")
    h = r["headers_seguridad"]
    checks = [
        ("x_frame_options", "Protección Clickjacking (X-Frame-Options)"),
        ("x_content_type_options", "Protección MIME Sniffing"),
        ("strict_transport_security", "HSTS (Forzar HTTPS)"),
        ("content_security_policy", "Content Security Policy (CSP)"),
        ("referrer_policy", "Referrer Policy"),
        ("permissions_policy", "Permissions Policy"),
        ("x_xss_protection", "Protección XSS")
    ]
    for key, nombre in checks:
        if h[key]["presente"]:
            lines.append(f"  ✅ {nombre}")
        else:
            lines.append(f"  ⚠️ {nombre} - NO CONFIGURADO")
    lines.append("")
    
    # Cookies
    lines.append("🍪 COOKIES")
    c = r["cookies"]
    lines.append(f"  Total: {c['total']}")
    if c["inseguras"]:
        lines.append(f"  ⚠️ Cookies inseguras: {', '.join(c['inseguras'])}")
    else:
        lines.append(f"  ✅ Todas las cookies son seguras")
    lines.append("")
    
    # Tecnologías
    if r["tecnologias"]:
        lines.append("🔧 TECNOLOGÍAS DETECTADAS")
        for t in r["tecnologias"]:
            lines.append(f"  • {t}")
        lines.append("")
    
    # Archivos expuestos
    lines.append("📁 ARCHIVOS EXPUESTOS")
    if r["archivos_expuestos"]:
        for a in r["archivos_expuestos"]:
            lines.append(f"  ⚠️ /{a}")
    else:
        lines.append("  ✅ No se detectaron archivos sensibles")
    lines.append("")
    
    # Puertos
    lines.append("🔌 PUERTOS ABIERTOS")
    for p in r["puertos_abiertos"]:
        lines.append(f"  • Puerto {p}")
    lines.append("")
    
    # Recomendaciones
    lines.append(" RECOMENDACIONES")
    recomendaciones = []
    if not r["https"]:
        recomendaciones.append("1. Instalar certificado SSL (Let's Encrypt es gratis)")
    if not h["x_frame_options"]["presente"]:
        recomendaciones.append("2. Agregar header X-Frame-Options: DENY")
    if not h["content_security_policy"]["presente"]:
        recomendaciones.append("3. Configurar Content Security Policy")
    if len(c["inseguras"]) > 0:
        recomendaciones.append("4. Marcar cookies sensibles como Secure y HttpOnly")
    if len(r["archivos_expuestos"]) > 0:
        recomendaciones.append("5. Eliminar o proteger archivos sensibles expuestos")
    
    if recomendaciones:
        for rec in recomendaciones:
            lines.append(f"  {rec}")
    else:
        lines.append("  ✅ Tu sitio tiene buena configuración de seguridad")
    
    return "\n".join(lines)

from datetime import datetime

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a Atlasec API - Escáner de seguridad v2.0"}