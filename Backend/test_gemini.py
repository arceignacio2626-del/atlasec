import os
import google.generativeai as genai
from dotenv import load_dotenv

print("🔍 Diagnóstico de Gemini API\n")

# 1. Verificar .env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No se encontró GEMINI_API_KEY en .env")
    print("   Verifica que el archivo .env exista y tenga:")
    print("   GEMINI_API_KEY=tu_clave")
else:
    print(f"✅ API Key encontrada: {api_key[:10]}...")
    
    # 2. Configurar Gemini
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini configurado correctamente")
        
        # 3. Listar modelos disponibles
        print("\n📋 Modelos disponibles:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"   - {model.name}")
        
        # 4. Probar con el primer modelo disponible
        print("\n🧪 Probando generación de contenido...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Di solo 'Hola desde Gemini'")
        print(f"✅ Respuesta: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPosibles causas:")
        print("1. La API Key es inválida")
        print("2. No activaste la API en Google Cloud Console")
        print("3. La clave no tiene permisos")