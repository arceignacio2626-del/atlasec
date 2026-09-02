# ============================================
# ATLASEC API - Backend Principal
# Versión 2.2 con Rate Limiting y Seguridad
# ============================================

# --- IMPORTACIONES ---
# DEPLOY v2.2.1 - Forzado: [fecha de hoy]
from fastapi import FastAPI, HTTPException, Request
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import scanner
import re
import socket
import ipaddress
from urllib.parse import urlparse
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atlasec")

# --- INICIALIZAR APP ---
app = FastAPI(
    title="Atlasec API",
    description="API de escaneo de seguridad para PYMEs - Versión 2.2",
    version="2.2.0"
)

# --- CONFIGURACIÓN DE RATE LIMITING ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://atlasec.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS ---
class SolicitudEscaneo(BaseModel):
    url: str

# --- FUNCIONES DE VALIDACIÓN ---
def validar_formato_url(url: str) -> bool:
    """Valida que la URL tenga un formato correcto"""
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return bool(re.match(pattern, url))

def es_url_segura(url: str) -> bool:
    """Valida que la URL no apunte a IPs privadas o localhost"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False
        
        # Bloquear localhost y variantes
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            return False
        
        # Bloquear IPs privadas
        try:
            ip = socket.gethostbyname(hostname)
            if ipaddress.ip_address(ip).is_private:
                return False
        except socket.gaierror:
            # Si no puede resolver el dominio, dejar pasar (el scanner fallará después)
            pass
        
        return True
    except Exception:
        return False

# --- ENDPOINTS ---

@app.get("/")
def root():
    """Endpoint raíz - Información de la API"""
    return {
        "mensaje": "Atlasec API v2.2 - Escáner de Seguridad Web",
        "documentacion": "/docs",
        "version": "2.2.0"
    }

@app.get("/health")
def health_check():
    """Verifica que la API esté funcionando"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.2.0"
    }

@app.post("/escanear")
@limiter.limit("5/minute")  # Rate limit: 5 escaneos por minuto por IP
def escanear_sitio(request: Request, solicitud: SolicitudEscaneo):
    """
    Escanea un sitio web en busca de vulnerabilidades de seguridad.
    Límite: 5 escaneos por minuto por dirección IP.
    """
    url = solicitud.url.strip()
    
    # Registrar el intento de escaneo
    client_ip = request.client.host if request.client else "desconocido"
    logger.info(f"Escaneo solicitado: {url} desde IP: {client_ip}")
    
    # Validar que no esté vacío
    if not url:
        logger.warning(f"URL vacía desde IP: {client_ip}")
        return {
            "success": False,
            "error": "La URL no puede estar vacía"
        }
    
    # Agregar protocolo si falta
    if not url.startswith('http'):
        url = 'https://' + url
    
    # Validar formato
    if not validar_formato_url(url):
        logger.warning(f"URL con formato inválido: {url} desde IP: {client_ip}")
        return {
            "success": False,
            "error": "Formato de URL inválido. Ejemplo: https://google.com"
        }
    
    # Validar seguridad (no IPs privadas)
    if not es_url_segura(url):
        logger.warning(f"Intento de escaneo a IP privada: {url} desde IP: {client_ip}")
        return {
            "success": False,
            "error": "No se permite escanear direcciones IP privadas o localhost"
        }
    
    # Realizar escaneo
    logger.info(f"Iniciando escaneo de: {url}")
    resultados = scanner.escanear_seguridad(url)
    
    if "error" in resultados:
        logger.error(f"Error al escanear {url}: {resultados['error']}")
        return {
            "success": False,
            "error": resultados["error"]
        }
    
    # Generar reporte
    reporte = generar_reporte(resultados)
    
    logger.info(f"Escaneo completado: {url} - Score: {resultados.get('score', 'N/A')}")
    
    return {
        "success": True,
        "url": resultados["url"],
        "score": resultados["score"],
        "nivel_riesgo": resultados["nivel_riesgo"],
        "resultados": resultados,
        "reporte": reporte
    }

# --- GENERADOR DE REPORTE ---
def generar_reporte(r):
    """Genera reporte completo y profesional"""
    lines = []
    lines.append("=" * 60)
    lines.append(f"REPORTE DE SEGURIDAD - Atlasec v2.2")
    lines.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lines.append(f"URL Analizada: {r['url']}")
    lines.append(f"Score de Seguridad: {r['score']}/100")
    lines.append(f"Nivel de Riesgo: {r['nivel_riesgo'].upper()}")
    lines.append("=" * 60)
    lines.append("")
    
    # RESUMEN EJECUTIVO
    lines.append("📊 RESUMEN EJECUTIVO")
    lines.append("-" * 60)
    if r['score'] >= 80:
        lines.append("✅ Tu sitio tiene un BUEN nivel de seguridad")
    elif r['score'] >= 60:
        lines.append("️ Tu sitio necesita MEJORAS de seguridad")
    else:
        lines.append("❌ Tu sitio tiene PROBLEMAS GRAVES de seguridad")
    lines.append("")
    
    # HTTPS
    lines.append("🔒 CONEXIÓN SEGURA (HTTPS)")
    if r["https"]:
        lines.append("  ✅ Sitio usa HTTPS")
        if r.get("ssl", {}).get("valido"):
            ssl_info = r["ssl"]
            lines.append(f"  ✅ Certificado SSL válido")
            lines.append(f"   Emisor: {ssl_info.get('emisor', 'N/A')}")
            lines.append(f"  📅 Expira: {ssl_info.get('expira', 'N/A')}")
            dias = ssl_info.get('dias_restantes', 999)
            if dias < 30:
                lines.append(f"  ⚠️ ALERTA: Expira en {dias} días")
            else:
                lines.append(f"  ✅ Días restantes: {dias}")
    else:
        lines.append("  ❌ Sitio NO usa HTTPS (RIESGO CRÍTICO)")
        lines.append("     Los datos viajan sin encriptar")
    lines.append("")
    
    # HEADERS DE SEGURIDAD
    lines.append("🛡️ HEADERS DE SEGURIDAD")
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
            lines.append(f"  ❌ {nombre} - NO CONFIGURADO")
    lines.append("")
    
    # COOKIES
    lines.append("🍪 COOKIES")
    c = r["cookies"]
    lines.append(f"  Total de cookies: {c['total']}")
    if c["inseguras"]:
        lines.append(f"  ⚠️ Cookies SIN flag Secure: {', '.join(c['inseguras'][:3])}")
        lines.append(f"     Riesgo: Pueden ser interceptadas en conexiones no seguras")
    else:
        lines.append(f"  ✅ Todas las cookies tienen flag Secure")
    lines.append("")
    
    # TECNOLOGÍAS
    if r["tecnologias"]:
        lines.append("🔧 TECNOLOGÍAS DETECTADAS")
        for t in r["tecnologias"]:
            lines.append(f"  • {t}")
        lines.append("")
    
    # VULNERABILIDADES
    lines.append("🚨 VULNERABILIDADES DETECTADAS")
    if r["vulnerabilidades"]:
        criticas = [v for v in r["vulnerabilidades"] if v["tipo"] == "crítico"]
        altas = [v for v in r["vulnerabilidades"] if v["tipo"] == "alto"]
        medias = [v for v in r["vulnerabilidades"] if v["tipo"] == "medio"]
        bajas = [v for v in r["vulnerabilidades"] if v["tipo"] == "bajo"]
        info = [v for v in r["vulnerabilidades"] if v["tipo"] == "info"]
        
        if criticas:
            lines.append(f"  🔴 CRÍTICAS ({len(criticas)}):")
            for v in criticas:
                lines.append(f"     • {v['descripcion']}")
        
        if altas:
            lines.append(f"  🟠 ALTAS ({len(altas)}):")
            for v in altas:
                lines.append(f"     • {v['descripcion']}")
        
        if medias:
            lines.append(f"  🟡 MEDIAS ({len(medias)}):")
            for v in medias:
                lines.append(f"     • {v['descripcion']}")
        
        if bajas:
            lines.append(f"  🔵 BAJAS ({len(bajas)}):")
            for v in bajas:
                lines.append(f"     • {v['descripcion']}")
        
        if info:
            lines.append(f"  ℹ️ INFO ({len(info)}):")
            for v in info:
                lines.append(f"     • {v['descripcion']}")
    else:
        lines.append("  ✅ No se detectaron vulnerabilidades significativas")
    lines.append("")
    
    # ARCHIVOS EXPUESTOS
    lines.append("📁 ARCHIVOS EXPUESTOS")
    if r["archivos_expuestos"]:
        for a in r["archivos_expuestos"]:
            riesgo = "🔴" if a in ['.env', '.git/config', 'backup.sql', '.htpasswd', 'config.php'] else "⚠️"
            lines.append(f"  {riesgo} /{a}")
    else:
        lines.append("  ✅ No se detectaron archivos sensibles expuestos")
    lines.append("")
    
    # RECOMENDACIONES PRIORIZADAS
    lines.append("💡 PLAN DE ACCIÓN PRIORIZADO")
    lines.append("-" * 60)
    
    recomendaciones = []
    if not r["https"]:
        recomendaciones.append(("1", "CRÍTICO", "Instalar certificado SSL (Let's Encrypt es gratuito)"))
    if r.get("ssl", {}).get("valido") == False:
        recomendaciones.append(("2", "CRÍTICO", "Renovar certificado SSL expirado"))
    if not h["x_frame_options"]["presente"]:
        recomendaciones.append(("3", "ALTO", "Agregar header: X-Frame-Options: DENY o SAMEORIGIN"))
    if not h["content_security_policy"]["presente"]:
        recomendaciones.append(("4", "MEDIO", "Configurar Content Security Policy"))
    if len(c["inseguras"]) > 0:
        recomendaciones.append(("5", "MEDIO", "Marcar cookies como Secure y HttpOnly"))
    if len(r["archivos_expuestos"]) > 0:
        recomendaciones.append(("6", "ALTO", "Eliminar o proteger archivos sensibles"))
    if not h["strict_transport_security"]["presente"] and r["https"]:
        recomendaciones.append(("7", "MEDIO", "Agregar HSTS: Strict-Transport-Security: max-age=31536000"))
    
    if recomendaciones:
        for num, prioridad, rec in recomendaciones:
            lines.append(f"  {num}. [{prioridad}] {rec}")
    else:
        lines.append("  ✅ Tu sitio tiene excelente configuración de seguridad")
        lines.append("     ¡Sigue así!")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("Reporte generado por Atlasec - Seguridad Web con IA")
    lines.append("¿Necesitas ayuda? contacto@atlasec.lat")
    lines.append("=" * 60)
    
    return "\n".join(lines)

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)