"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [reporte, setReporte] = useState("");
  const [error, setError] = useState("");
  const [score, setScore] = useState<number | null>(null);
  
  // Estados de autenticación
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<any>(null);
  const [loadingAuth, setLoadingAuth] = useState(false);

  // Verificar sesión al cargar
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Función de autenticación
  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingAuth(true);

    try {
      if (authMode === 'login') {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        setUser(data.user);
        setShowAuth(false);
      } else {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        alert('✅ Cuenta creada! Ya estás logueado.');
        setUser(data.user);
        setShowAuth(false);
      }
    } catch (error: any) {
      alert('❌ Error: ' + error.message);
    } finally {
      setLoadingAuth(false);
    }
  };

  // Logout
  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  // Guardar escaneo en Supabase
  const guardarEscaneo = async (resultado: any) => {
    if (!user) {
      setShowAuth(true);
      return false;
    }

    try {
      const { error } = await supabase
        .from('scans')
        .insert({
          user_id: user.id,
          url: resultado.url,
          score: resultado.score,
          nivel_riesgo: resultado.nivel_riesgo,
          resultados: resultado.resultados,
          reporte: resultado.reporte,
        });

      if (error) throw error;
      console.log('✅ Escaneo guardado');
      return true;
    } catch (error: any) {
      console.error('Error guardando escaneo:', error);
      return false;
    }
  };

  // Escanear sitio
  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setReporte("");
    setScore(null);

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
        setScore(data.score || 0);
        setReporte(data.reporte);
        await guardarEscaneo(data);
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
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Navigation */}
      <nav className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-[#0a0a0f]/90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
              <span className="text-2xl font-bold">Atlasec</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-300 hover:text-white transition">Features</a>
              <a href="#pricing" className="text-gray-300 hover:text-white transition">Pricing</a>
              <a href="#about" className="text-gray-300 hover:text-white transition">About</a>
              
              {user ? (
                <div className="flex items-center gap-4">
                  <span className="text-gray-300 text-sm">{user.email}</span>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 border border-white/20 rounded-lg hover:bg-white/5 transition"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <>
                  <button
                    onClick={() => setShowAuth(true)}
                    className="px-4 py-2 text-gray-300 hover:text-white transition"
                  >
                    Login
                  </button>
                  <button className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition">
                    Start for Free
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-32 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
            Secure everything devs
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
              build, ship and run
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-12 max-w-3xl mx-auto">
            Continuous, autonomous security that gets developers back to building.
            Escanea tu sitio web y detecta vulnerabilidades en segundos.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition">
              Start for Free
            </button>
            <button className="px-8 py-4 border border-white/20 rounded-lg font-semibold text-lg hover:bg-white/5 transition">
              Book a Demo
            </button>
          </div>

          {/* Trust Badge */}
          <p className="text-gray-500 text-sm">
            Trusted by 150+ orgs | See results in 30sec
          </p>
        </div>
      </section>

      {/* Live Scanner Section */}
      <section className="py-20 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0f]">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-8">
            Try it now - Free Security Scan
          </h2>
          <p className="text-gray-400 text-center mb-12">
            Escanea tu sitio web y obtén un reporte completo de seguridad en segundos
          </p>

          <form onSubmit={handleScan} className="space-y-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <input
                type="text"
                placeholder="Ingresa la URL de tu sitio (ej: google.com)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1 px-6 py-4 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-500"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition disabled:opacity-50"
              >
                {loading ? "🔍 Escaneando..." : "🛡️ Escanear"}
              </button>
            </div>
          </form>

          {/* Score Display */}
          {score !== null && (
            <div className="mt-8 p-6 bg-white/5 border border-white/10 rounded-lg">
              <div className="text-center">
                <div className={`text-6xl font-bold mb-2 ${
                  score >= 80 ? "text-green-500" :
                  score >= 60 ? "text-yellow-500" :
                  score >= 40 ? "text-orange-500" : "text-red-500"
                }`}>
                  {score}/100
                </div>
                <p className="text-gray-400">Security Score</p>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-red-400">⚠️ {error}</p>
            </div>
          )}

          {/* Report Display */}
          {reporte && (
            <div className="mt-6 p-6 bg-white/5 border border-white/10 rounded-lg">
              <h3 className="text-xl font-semibold mb-4 text-green-400">✅ Security Report</h3>
              <pre className="whitespace-pre-wrap text-gray-300 text-sm text-left max-h-96 overflow-y-auto">
                {reporte}
              </pre>
            </div>
          )}
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 bg-[#0a0a0f]">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">
            Everything you need to secure your stack
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-white/5 border border-white/10 rounded-xl hover:border-blue-500/50 transition">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg mb-4"></div>
              <h3 className="text-xl font-semibold mb-3">Web Security Scanning</h3>
              <p className="text-gray-400">Automated vulnerability scanning for web applications. Detect SSL issues, security headers, and more.</p>
            </div>

            <div className="p-6 bg-white/5 border border-white/10 rounded-xl hover:border-purple-500/50 transition">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg mb-4"></div>
              <h3 className="text-xl font-semibold mb-3">AI-Powered Analysis</h3>
              <p className="text-gray-400">Intelligent risk assessment and prioritized recommendations powered by machine learning.</p>
            </div>

            <div className="p-6 bg-white/5 border border-white/10 rounded-xl hover:border-green-500/50 transition">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg mb-4"></div>
              <h3 className="text-xl font-semibold mb-3">Continuous Monitoring</h3>
              <p className="text-gray-400">24/7 automated scanning and alerting. Never miss a critical vulnerability.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-[#0f0f1a]">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-4">Simple, transparent pricing</h2>
          <p className="text-gray-400 text-center mb-16">Start free, upgrade when you need more</p>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Free Plan */}
            <div className="p-8 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-2xl font-semibold mb-2">Free</h3>
              <div className="text-4xl font-bold mb-6">$0<span className="text-lg text-gray-400 font-normal">/mo</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">1 scan/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Basic report</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Email support</span>
                </li>
              </ul>
              <button className="w-full py-3 border border-white/20 rounded-lg font-semibold hover:bg-white/5 transition">
                Get Started
              </button>
            </div>

            {/* Pro Plan */}
            <div className="p-8 bg-gradient-to-b from-blue-600/20 to-purple-600/20 border border-blue-500/50 rounded-xl relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full text-sm font-semibold">
                Most Popular
              </div>
              <h3 className="text-2xl font-semibold mb-2">Pro</h3>
              <div className="text-4xl font-bold mb-6">$29<span className="text-lg text-gray-400 font-normal">/mo</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">50 scans/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">PDF reports</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Continuous monitoring</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Priority support</span>
                </li>
              </ul>
              <button className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition">
                Start Free Trial
              </button>
            </div>

            {/* Enterprise Plan */}
            <div className="p-8 bg-white/5 border border-white/10 rounded-xl">
              <h3 className="text-2xl font-semibold mb-2">Enterprise</h3>
              <div className="text-4xl font-bold mb-6">$99<span className="text-lg text-gray-400 font-normal">/mo</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Unlimited scans</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">API access</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Custom integrations</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-300">Dedicated support</span>
                </li>
              </ul>
              <button className="w-full py-3 border border-white/20 rounded-lg font-semibold hover:bg-white/5 transition">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0f]">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold mb-6">
            Ready to secure your applications?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join 150+ organizations trusting Atlasec for their security needs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition">
              Start for Free
            </button>
            <button className="px-8 py-4 border border-white/20 rounded-lg font-semibold text-lg hover:bg-white/5 transition">
              Talk to Sales
            </button>
          </div>
        </div>
      </section>

      {/* Auth Modal */}
      {showAuth && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#0f0f1a] border border-white/10 rounded-xl p-8 max-w-md w-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">
                {authMode === 'login' ? 'Login' : 'Sign Up'}
              </h2>
              <button
                onClick={() => setShowAuth(false)}
                className="text-gray-400 hover:text-white"
              >
                
              </button>
            </div>

            <form onSubmit={handleAuth} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loadingAuth}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition disabled:opacity-50"
              >
                {loadingAuth ? 'Loading...' : authMode === 'login' ? 'Login' : 'Sign Up'}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                onClick={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
                className="text-blue-400 hover:text-blue-300 text-sm"
              >
                {authMode === 'login' 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Login"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-[#0a0a0f]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
                <span className="text-xl font-bold">Atlasec</span>
              </div>
              <p className="text-gray-400 text-sm">
                Continuous, autonomous security for modern development teams.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition">Features</a></li>
                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">API</a></li>
                <li><a href="#" className="hover:text-white transition">Integrations</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Careers</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 text-center text-gray-400 text-sm">
            <p>© 2026 Atlasec. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}