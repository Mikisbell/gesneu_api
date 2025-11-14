export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          🚗 GesNeu API
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Sistema de Gestión de Neumáticos
        </p>
        <div className="space-y-4">
          <div className="bg-green-100 p-4 rounded-lg">
            <p className="text-green-800">✅ Next.js + TypeScript</p>
          </div>
          <div className="bg-blue-100 p-4 rounded-lg">
            <p className="text-blue-800">✅ Supabase PostgreSQL</p>
          </div>
          <div className="bg-purple-100 p-4 rounded-lg">
            <p className="text-purple-800">✅ Prisma ORM</p>
          </div>
        </div>
        <div className="mt-8">
          <a 
            href="/api/health" 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            🔍 Test API Health
          </a>
        </div>
      </div>
    </main>
  )
}
