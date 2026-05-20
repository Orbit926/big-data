import { ArrowLeftIcon } from './Icons'

export default function AuthShell({ children, onBack }) {
  return (
    <div className="min-h-screen bg-gris-claro flex flex-col">
      <header className="px-6 py-4">
        {onBack && (
          <button
            className="w-12 h-12 rounded-full bg-white shadow-md flex items-center justify-center text-azul-oscuro font-bold text-xl hover:bg-gray-100 transition-colors"
            aria-label="Volver atras"
            onClick={onBack}
          >
            <ArrowLeftIcon className="h-6 w-6" />
          </button>
        )}
      </header>
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        {children}
      </main>
    </div>
  )
}
