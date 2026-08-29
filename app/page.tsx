export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="text-2xl font-bold text-white">
            Atlas<span className="text-blue-400">ec</span>
          </div>
          <a
            href="#contacto"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition"
          >
            Empezar
          </a>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Seguridad Web con IA para tu PYME
          </h1>
          <p className="text-xl text-slate-300 mb-8 leading-relaxed">
            Escaneamos tu sitio web y te entregamos un reporte claro en español, 
            sin tecnicismos. Descubre tus vulnerabilidades y cómo solucionarlas hoy.
          </p>
          
          {/* Formulario de Email */}
          <div id="contacto" className="max-w-md mx-auto">
            <form className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                placeholder="tu@email.com"
                className="flex-1 px-4 py-3 rounded-lg bg-slate-800 text-white border border-slate-700 focus:outline-none focus:border-blue-500"
                required
              />
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition whitespace-nowrap"
              >
                Probar Gratis
              </button>
            </form>
            <p className="text-sm text-slate-400 mt-4">
              Sin tarjeta de crédito. Resultados en 2 minutos.
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20 max-w-5xl mx-auto">
          <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
            <div className="text-4xl mb-4">🛡️</div>
            <h3 className="text-xl font-bold text-white mb-2">Escaneo Automático</h3>
            <p className="text-slate-300">
              Analizamos tu web en busca de vulnerabilidades críticas en segundos.
            </p>
          </div>
          
          <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold text-white mb-2">Reporte con IA</h3>
            <p className="text-slate-300">
              Te explicamos los riesgos en lenguaje simple, sin jerga técnica.
            </p>
          </div>
          
          <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
            <div className="text-4xl mb-4">✅</div>
            <h3 className="text-xl font-bold text-white mb-2">Plan de Acción</h3>
            <p className="text-slate-300">
              Pasos claros para solucionar cada problema encontrado.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-20 border-t border-slate-800">
        <p className="text-center text-slate-400">
          © 2024 Atlasec. Seguridad inteligente para PYMEs.
        </p>
      </footer>
    </div>
  )
}