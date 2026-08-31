import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import re

def escanear_seguridad(url):
    """
    Escaneo completo de seguridad web - Versión 2.1 (Corregido)
    """
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Atlasec Security Scanner/2.1'
        }
        
        # Aumentar timeout a 15 segundos
        response = requests.get(url, timeout=15, allow_redirects=True, headers=headers, verify=True)
        
        resultados = {
            "url": url,
            "url_final": response.url,
            "codigo_estado": response.status_code,
            "tiempo_respuesta_ms": response.elapsed.total_seconds() * 1000,
            "https": False,
            "redireccion_https": False,
            "ssl": {},
            "headers_seguridad": {},
            "cookies": {},
            "tecnologias": [],
            "archivos_expuestos": [],
            "vulnerabilidades": [],
            "score": 0,
            "nivel_riesgo": "Bajo"
        }
        
        # 1. HTTPS y redirección
        parsed = urlparse(url)
        resultados["https"] = parsed.scheme == 'https'
        resultados["redireccion_https"] = 'https' in response.url
        
        if not resultados["https"]:
            resultados["vulnerabilidades"].append({
                "tipo": "crítico",
                "descripcion": "Sitio no usa HTTPS",
                "solucion": "Instalar certificado SSL (Let's Encrypt es gratuito)"
            })
        
        # 2. Certificado SSL
        if resultados["https"]:
            resultados["ssl"] = verificar_ssl(parsed.hostname)
            if not resultados["ssl"].get("valido"):
                resultados["vulnerabilidades"].append({
                    "tipo": "alto",
                    "descripcion": "Certificado SSL inválido o expirado",
                    "solucion": "Renovar o instalar certificado SSL válido"
                })
        
        # 3. Headers de Seguridad
        resp_headers = response.headers
        resultados["headers_seguridad"] = {
            "x_frame_options": {
                "presente": 'X-Frame-Options' in resp_headers,
                "valor": resp_headers.get('X-Frame-Options', 'No configurado')
            },
            "x_content_type_options": {
                "presente": 'X-Content-Type-Options' in resp_headers,
                "valor": resp_headers.get('X-Content-Type-Options', 'No configurado')
            },
            "strict_transport_security": {
                "presente": 'Strict-Transport-Security' in resp_headers,
                "valor": resp_headers.get('Strict-Transport-Security', 'No configurado')
            },
            "content_security_policy": {
                "presente": 'Content-Security-Policy' in resp_headers,
                "valor": resp_headers.get('Content-Security-Policy', 'No configurado')
            },
            "referrer_policy": {
                "presente": 'Referrer-Policy' in resp_headers,
                "valor": resp_headers.get('Referrer-Policy', 'No configurado')
            },
            "permissions_policy": {
                "presente": 'Permissions-Policy' in resp_headers,
                "valor": resp_headers.get('Permissions-Policy', 'No configurado')
            },
            "x_xss_protection": {
                "presente": 'X-XSS-Protection' in resp_headers,
                "valor": resp_headers.get('X-XSS-Protection', 'No configurado')
            }
        }
        
        # Verificar vulnerabilidades en headers
        if not resultados["headers_seguridad"]["x_frame_options"]["presente"]:
            resultados["vulnerabilidades"].append({
                "tipo": "medio",
                "descripcion": "Falta header X-Frame-Options",
                "solucion": "Agregar header: X-Frame-Options: DENY o SAMEORIGIN"
            })
        
        if not resultados["headers_seguridad"]["content_security_policy"]["presente"]:
            resultados["vulnerabilidades"].append({
                "tipo": "medio",
                "descripcion": "Falta Content Security Policy (CSP)",
                "solucion": "Configurar header Content-Security-Policy"
            })
        
        if not resultados["headers_seguridad"]["x_content_type_options"]["presente"]:
            resultados["vulnerabilidades"].append({
                "tipo": "bajo",
                "descripcion": "Falta X-Content-Type-Options",
                "solucion": "Agregar header: X-Content-Type-Options: nosniff"
            })
        
        # 4. Cookies seguras
        cookies_inseguras = []
        for cookie in response.cookies:
            if not cookie.secure:
                cookies_inseguras.append(cookie.name)
        
        resultados["cookies"] = {
            "total": len(response.cookies),
            "inseguras": cookies_inseguras,
            "seguras": len(response.cookies) - len(cookies_inseguras)
        }
        
        if len(cookies_inseguras) > 0:
            resultados["vulnerabilidades"].append({
                "tipo": "medio",
                "descripcion": f"Cookies sin flag Secure: {', '.join(cookies_inseguras[:3])}",
                "solucion": "Marcar cookies sensibles como Secure y HttpOnly"
            })
        
        # 5. Tecnologías detectadas (CORREGIDO - menos falsos positivos)
        server = resp_headers.get('Server', '')
        if server:
            resultados["tecnologias"].append(f"Servidor web: {server}")
        
        # Detectar CMS y frameworks con patrones más específicos
        html_content = response.text
        
        # WordPress: buscar patrones específicos, no solo texto
        if re.search(r'wp-content|wp-includes|wordpress\.org', html_content, re.IGNORECASE):
            resultados["tecnologias"].append("WordPress detectado")
            resultados["vulnerabilidades"].append({
                "tipo": "info",
                "descripcion": "WordPress detectado - Mantener actualizado",
                "solucion": "Actualizar WordPress, temas y plugins regularmente"
            })
        
        # Shopify: buscar patrones específicos
        if re.search(r'shopify\.com|cdn\.shopify\.com', html_content, re.IGNORECASE):
            resultados["tecnologias"].append("Shopify detectado")
        
        # React: buscar patrones específicos
        if re.search(r'react|__NEXT_DATA__|react-dom', html_content, re.IGNORECASE):
            resultados["tecnologias"].append("React/Next.js detectado")
        
        # 6. Archivos expuestos (CORREGIDO - verificar contenido real)
        archivos_peligrosos = [
            '.env', 'robots.txt', 'wp-login.php', 'wp-admin', 
            '.git/config', 'phpinfo.php', 'info.php',
            'backup.sql', 'database.sql', '.htaccess',
            'xmlrpc.php', 'readme.html', 'config.php',
            '.htpasswd', 'phpmyadmin', 'admin.php'
        ]
        
        for archivo in archivos_peligrosos:
            url_archivo = f"{url.rstrip('/')}/{archivo}"
            try:
                res_archivo = requests.get(url_archivo, timeout=5, allow_redirects=False, headers=headers)
                
                # Solo reportar si realmente existe (status 200 y contenido no vacío)
                if res_archivo.status_code == 200 and len(res_archivo.text) > 0:
                    # Verificar que no sea una página de error o redirección
                    if '404' not in res_archivo.text[:500] and 'not found' not in res_archivo.text[:500].lower():
                        resultados["archivos_expuestos"].append(archivo)
                        
                        # Archivos críticos
                        if archivo in ['.env', '.git/config', 'backup.sql', '.htpasswd', 'config.php']:
                            resultados["vulnerabilidades"].append({
                                "tipo": "crítico",
                                "descripcion": f"Archivo sensible expuesto: {archivo}",
                                "solucion": f"Eliminar o proteger /{archivo} inmediatamente"
                            })
            except:
                pass
        
        # 7. Calcular score de seguridad
        score = 100
        
        if not resultados["https"]:
            score -= 30
        if resultados["ssl"] and not resultados["ssl"].get("valido"):
            score -= 25
        if not resultados["headers_seguridad"]["x_frame_options"]["presente"]:
            score -= 10
        if not resultados["headers_seguridad"]["x_content_type_options"]["presente"]:
            score -= 5
        if not resultados["headers_seguridad"]["strict_transport_security"]["presente"]:
            score -= 10
        if not resultados["headers_seguridad"]["content_security_policy"]["presente"]:
            score -= 15
        if not resultados["headers_seguridad"]["referrer_policy"]["presente"]:
            score -= 5
        if len(cookies_inseguras) > 0:
            score -= 10
        if len(resultados["archivos_expuestos"]) > 3:
            score -= 15
        elif len(resultados["archivos_expuestos"]) > 0:
            score -= 5
        
        # Vulnerabilidades críticas restan más
        vulns_criticas = len([v for v in resultados["vulnerabilidades"] if v["tipo"] == "crítico"])
        vulns_altas = len([v for v in resultados["vulnerabilidades"] if v["tipo"] == "alto"])
        
        score -= (vulns_criticas * 10)
        score -= (vulns_altas * 5)
        
        resultados["score"] = max(0, min(100, score))
        
        # Determinar nivel de riesgo
        if score >= 80:
            resultados["nivel_riesgo"] = "Bajo"
        elif score >= 60:
            resultados["nivel_riesgo"] = "Medio"
        elif score >= 40:
            resultados["nivel_riesgo"] = "Alto"
        else:
            resultados["nivel_riesgo"] = "Crítico"
        
        return resultados

    except requests.exceptions.SSLError as e:
        return {
            "error": "Error de SSL - El certificado puede ser inválido",
            "score": 0,
            "nivel_riesgo": "Crítico"
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "No se pudo conectar al sitio - Verifica la URL",
            "score": 0,
            "nivel_riesgo": "Crítico"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Timeout - El sitio tardó demasiado en responder",
            "score": 0,
            "nivel_riesgo": "Desconocido"
        }
    except Exception as e:
        return {"error": str(e), "score": 0, "nivel_riesgo": "Desconocido"}


def verificar_ssl(hostname):
    """Verifica el certificado SSL del sitio."""
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            
            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            dias_restantes = (not_after - datetime.utcnow()).days
            
            return {
                "valido": True,
                "emisor": dict(x[0] for x in cert['issuer'])['commonName'],
                "sujeto": dict(x[0] for x in cert['subject']).get('commonName', 'N/A'),
                "expira": cert['notAfter'],
                "dias_restantes": dias_restantes,
                "version": cert['version'],
                "alerta_expiracion": dias_restantes < 30
            }
    except ssl.CertificateError as e:
        return {"valido": False, "error": f"Error de certificado: {str(e)}"}
    except Exception as e:
        return {"valido": False, "error": str(e)}