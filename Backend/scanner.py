import requests

def escanear_seguridad(url):
    """
    Escanea una URL y devuelve un diccionario con los resultados.
    """
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        response = requests.get(url, timeout=10)
        
        resultados = {
            "url": url,
            "https": False,
            "headers": {},
            "archivos_expuestos": []
        }
        
        # 1. HTTPS
        resultados["https"] = url.startswith('https://')
        
        # 2. Headers de Seguridad
        headers = response.headers
        resultados["headers"] = {
            "x_frame_options": 'X-Frame-Options' in headers,
            "x_content_type_options": 'X-Content-Type-Options' in headers,
            "strict_transport_security": 'Strict-Transport-Security' in headers
        }
        
        # 3. Archivos expuestos
        archivos_peligrosos = ['.env', 'robots.txt', 'wp-login.php', 'admin', '.git']
        for archivo in archivos_peligrosos:
            url_archivo = f"{url}/{archivo}"
            try:
                res_archivo = requests.get(url_archivo, timeout=5)
                if res_archivo.status_code == 200:
                    resultados["archivos_expuestos"].append(archivo)
            except:
                pass
        
        return resultados

    except Exception as e:
        return {"error": str(e)}