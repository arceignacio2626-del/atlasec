"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [reporte, setReporte] = useState("");
  const [error, setError] = useState("");

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setReporte("");

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/escanear`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.success) {
        setReporte(data.reporte);
      } else {
        setError(data.error || "Error al escanear el sitio");
      }
    } catch (err) {
      setError("No se pudo conectar con el servidor. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Atlasec
            </h1>
            <nav className="space-x-6">
              <a href="#inicio" className="hover:text-blue-400 transition">Inicio</a>
              <a href="#servicios" className="hover:text-blue-400 transition">Servicios</a>
              <a href="#contacto" className="hover:text-blue-400 transition">Contacto</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section id="inicio" className="pt-20 pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            Protege tu negocio con{" "}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Inteligencia Artificial
            </span>
          </h2>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Escaneo automático de vulnerabilidades web para PYMEs. 
            Detecta riesgos de seguridad antes que los hackers.
          </p>

          {/* Formulario de Escaneo */}
          <div className="max-w-2xl mx-auto bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <h3 className="text-2xl font-semibold mb-6">Prueba Gratis</h3>
            <form onSubmit={handleScan} className="space-y-4">
              <div>
                <input
                  type="text"
                  placeholder="Ingresa la URL de tu sitio web (ej: google.com)"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full px-6 py-4 bg-white/5 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg font-semibold hover:from-blue-700 hover:to-cyan-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "🔍 Escaneando..." : "🛡️ Escanear mi sitio"}
              </button>
            </form>

            {/* Mostrar Error */}
            {error && (
              <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
                <p className="text-red-300"> {error}</p>
              </div>
            )}

            {/* Mostrar Reporte */}
            {reporte && (
              <div className="mt-6 p-6 bg-green-500/10 border border-green-500/30 rounded-lg text-left">
                <h4 className="text-xl font-semibold mb-4 text-green-400">✅ Reporte de Seguridad</h4>
                <pre className="whitespace-pre-wrap text-gray-200 text-sm">
                  {reporte}
                </pre>
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-sm text-gray-400">
                    💡 ¿Necesitas ayuda para solucionar estos problemas? 
                    <a href="#contacto" className="text-blue-400 hover:underline ml-1">
                      Contáctanos
                    </a>
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Servicios */}
      <section id="servicios" className="py-20 bg-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-16">Nuestros Servicios</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-white/5 rounded-xl border border-white/10">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-3">Auditorías de Seguridad</h3>
              <p className="text-gray-400">Evaluación completa de vulnerabilidades en tu infraestructura web.</p>
            </div>
            <div className="p-6 bg-white/5 rounded-xl border border-white/10">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-3">IA Predictiva</h3>
              <p className="text-gray-400">Detección proactiva de amenazas usando machine learning.</p>
            </div>
            <div className="p-6 bg-white/5 rounded-xl border border-white/10">
              <div className="text-4xl mb-4">🛡️</div>
              <h3 className="text-xl font-semibold mb-3">Protección Continua</h3>
              <p className="text-gray-400">Monitoreo 24/7 de tu sitio web contra ataques.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Contacto */}
      <section id="contacto" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-8">¿Listo para proteger tu negocio?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Agenda una consultoría gratuita y descubre cómo podemos ayudarte.
          </p>
          <a 
            href="mailto:contacto@atlasec.lat" 
            className="inline-block px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg font-semibold hover:from-blue-700 hover:to-cyan-700 transition"
          >
            📧 contacto@atlasec.lat
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-400">
          <p>© 2026 Atlasec. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  );
}