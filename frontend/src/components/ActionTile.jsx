
export default function ActionTile({ label, icon: Icon }) {
  return (
    <button className="flex min-h-20 flex-col items-center justify-center gap-2 rounded-2xl border border-gray-100 bg-white text-sm shadow-sm">
      <Icon className="h-8 w-8 text-rojo-principal" />
      <span>{label}</span>
    </button>
  )
}
