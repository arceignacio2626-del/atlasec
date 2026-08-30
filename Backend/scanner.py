import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime

def escanear_seguridad(url):
    """
    Escaneo completo de seguridad web.
    """
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        
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
            "puertos_abiertos": [],
            "score": 0,
            "nivel_riesgo": "Bajo"
        }
        
        # 1. HTTPS
        parsed = urlparse(url)
        resultados["https"] = parsed.scheme == 'https'
        resultados["redireccion_https"] = 'https' in response.url
        
        # 2. Certificado SSL
        if resultados["https"]:
            resultados["ssl"] = verificar_ssl(parsed.hostname)
        
        # 3. Headers de Seguridad
        headers = response.headers
        resultados["headers_seguridad"] = {
            "x_frame_options": {
                "presente": 'X-Frame-Options' in headers,
                "valor": headers.get('X-Frame-Options', 'No configurado')
            },
            "x_content_type_options": {
                "presente": 'X-Content-Type-Options' in headers,
                "valor": headers.get('X-Content-Type-Options', 'No configurado')
            },
            "strict_transport_security": {
                "presente": 'Strict-Transport-Security' in headers,
                "valor": headers.get('Strict-Transport-Security', 'No configurado')
            },
            "content_security_policy": {
                "presente": 'Content-Security-Policy' in headers,
                "valor": headers.get('Content-Security-Policy', 'No configurado')
            },
            "referrer_policy": {
                "presente": 'Referrer-Policy' in headers,
                "valor": headers.get('Referrer-Policy', 'No configurado')
            },
            "permissions_policy": {
                "presente": 'Permissions-Policy' in headers,
                "valor": headers.get('Permissions-Policy', 'No configurado')
            },
            "x_xss_protection": {
                "presente": 'X-XSS-Protection' in headers,
                "valor": headers.get('X-XSS-Protection', 'No configurado')
            }
        }
        
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
        
        # 5. Tecnologías detectadas
        server = headers.get('Server', '')
        if server:
            resultados["tecnologias"].append(f"Servidor: {server}")
        
        if 'wordpress' in response.text.lower():
            resultados["tecnologias"].append("WordPress detectado")
        if 'shopify' in response.text.lower():
            resultados["tecnologias"].append("Shopify detectado")
        if 'wix' in response.text.lower():
            resultados["tecnologias"].append("Wix detectado")
        if 'react' in response.text.lower():
            resultados["tecnologias"].append("React detectado")
        
        # 6. Archivos expuestos
        archivos_peligrosos = [
            '.env', 'robots.txt', 'wp-login.php', 'wp-admin', 
            'admin', '.git/config', 'phpinfo.php', 'info.php',
            'backup.sql', 'database.sql', '.htaccess', 'sitemap.xml',
            'xmlrpc.php', 'readme.html', 'LICENSE.txt'
        ]
        for archivo in archivos_peligrosos:
            url_archivo = f"{url}/{archivo}"
            try:
                res_archivo = requests.get(url_archivo, timeout=3, allow_redirects=False)
                if res_archivo.status_code == 200:
                    resultados["archivos_expuestos"].append(archivo)
            except:
                pass
        
        # 7. Puertos abiertos (básico)
        hostname = parsed.hostname
        puertos_comunes = [80, 443, 21, 22, 3306, 5432, 8080, 8443]
        for puerto in puertos_comunes:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                resultado = sock.connect_ex((hostname, puerto))
                if resultado == 0:
                    resultados["puertos_abiertos"].append(puerto)
                sock.close()
            except:
                pass
        
        # 8. Calcular score de seguridad
        score = 100
        if not resultados["https"]:
            score -= 30
        if not resultados["headers_seguridad"]["x_frame_options"]["presente"]:
            score -= 10
        if not resultados["headers_seguridad"]["x_content_type_options"]["presente"]:
            score -= 10
        if not resultados["headers_seguridad"]["strict_transport_security"]["presente"]:
            score -= 10
        if not resultados["headers_seguridad"]["content_security_policy"]["presente"]:
            score -= 15
        if len(cookies_inseguras) > 0:
            score -= 10
        if len(resultados["archivos_expuestos"]) > 3:
            score -= 15
        elif len(resultados["archivos_expuestos"]) > 0:
            score -= 5
        
        resultados["score"] = max(0, score)
        
        if score >= 80:
            resultados["nivel_riesgo"] = "Bajo"
        elif score >= 60:
            resultados["nivel_riesgo"] = "Medio"
        elif score >= 40:
            resultados["nivel_riesgo"] = "Alto"
        else:
            resultados["nivel_riesgo"] = "Crítico"
        
        return resultados

    except Exception as e:
        return {"error": str(e)}


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
                "expira": cert['notAfter'],
                "dias_restantes": dias_restantes,
                "version": cert['version']
            }
    except Exception as e:
        return {"valido": False, "error": str(e)}