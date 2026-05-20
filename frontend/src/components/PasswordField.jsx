import { EyeIcon, EyeOffIcon } from './Icons'

export default function PasswordField({ value, showPassword, onChange, onToggle }) {
  return (
    <div className="relative">
      <input
        type={showPassword ? 'text' : 'password'}
        placeholder="**********"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-6 py-4 bg-white rounded-lg border-0 text-azul-oscuro placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rojo-principal"
      />
      <button
        type="button"
        onClick={onToggle}
        className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-azul-oscuro transition-colors"
        aria-label={showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'}
      >
        {showPassword ? <EyeIcon className="h-5 w-5" /> : <EyeOffIcon className="h-5 w-5" />}
      </button>
    </div>
  )
}
