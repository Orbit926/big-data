import { ArrowLeftIcon, GroupIcon } from './Icons'
import { travelCompanions, budgetOptions, travelStyles } from '../constants/travelData'

function PreferenceSection({ title, children }) {
  return (
    <section className="mt-10">
      <h2 className="mb-4 text-xl font-bold text-[#303244]">{title}</h2>
      {children}
    </section>
  )
}

function PillGroup({ options, selected, onSelect }) {
  return (
    <div className="flex flex-wrap justify-between gap-3 px-4">
      {options.map((option) => (
        <button
          key={option}
          className={`min-w-20 rounded-2xl border px-5 py-2.5 text-base transition-colors ${
            selected === option
              ? 'border-rojo-principal bg-rojo-principal text-white'
              : 'border-gray-200 bg-white text-[#20222f] shadow-sm hover:bg-gray-50'
          }`}
          onClick={() => onSelect(option)}
        >
          {option}
        </button>
      ))}
    </div>
  )
}

export default function TripPreferences({ preferences, setPreferences, onBack, onNext }) {
  const updatePreference = (key, value) => {
    setPreferences((current) => ({
      ...current,
      [key]: value,
    }))
  }

  const changeTravelers = (step) => {
    setPreferences((current) => ({
      ...current,
      travelers: Math.max(1, current.travelers + step),
    }))
  }

  return (
    <div className="min-h-screen bg-white text-[#303244]">
      <section className="relative h-56 overflow-hidden bg-gradient-to-r from-[#6d7087] via-[#cbdde4] to-[#8a90a6]">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white">
          <span className="text-5xl font-black tracking-[0.25em]">IMG</span>
          <span className="mt-3 text-sm font-semibold uppercase tracking-[0.2em] opacity-85">
            Espacio para imagen superior
          </span>
        </div>
        <button
          className="absolute left-8 top-10 grid h-16 w-16 place-items-center rounded-full bg-white text-[#20222f] shadow-lg"
          aria-label="Volver"
          onClick={onBack}
        >
          <ArrowLeftIcon className="h-8 w-8" />
        </button>
      </section>

      <main className="px-5 pb-8 pt-10">
        <h1 className="text-center text-4xl font-bold text-[#303244]">Cuentanos mas</h1>

        <PreferenceSection title="¿Con quien viajas?">
          <PillGroup
            options={travelCompanions}
            selected={preferences.companion}
            onSelect={(value) => updatePreference('companion', value)}
          />
        </PreferenceSection>

        <PreferenceSection title="¿Cuantas personas van?">
          <div className="mx-4 flex h-20 items-center justify-between rounded-2xl border border-gray-200 px-8 shadow-sm">
            <button
              className="grid h-10 w-10 place-items-center text-4xl leading-none text-[#303244]"
              aria-label="Quitar viajero"
              onClick={() => changeTravelers(-1)}
            >
              -
            </button>
            <p className="text-2xl font-bold text-[#303244]">
              {preferences.travelers} Viajeros
            </p>
            <button
              className="grid h-10 w-10 place-items-center text-4xl leading-none text-[#303244]"
              aria-label="Agregar viajero"
              onClick={() => changeTravelers(1)}
            >
              +
            </button>
          </div>
        </PreferenceSection>

        <PreferenceSection title="Presupuesto aproximado">
          <PillGroup
            options={budgetOptions}
            selected={preferences.budget}
            onSelect={(value) => updatePreference('budget', value)}
          />
        </PreferenceSection>

        <PreferenceSection title="Estilo de viaje">
          <PillGroup
            options={travelStyles}
            selected={preferences.style}
            onSelect={(value) => updatePreference('style', value)}
          />
        </PreferenceSection>

        <button
          className="mt-10 flex w-full items-center justify-between rounded-3xl border border-red-100 bg-red-50/40 px-6 py-5 text-left"
          onClick={() => updatePreference('jamGroup', !preferences.jamGroup)}
        >
          <div className="flex items-center gap-5">
            <span className="grid h-16 w-16 place-items-center rounded-full border border-red-100 bg-white text-rojo-principal">
              <GroupIcon className="h-8 w-8" />
            </span>
            <span>
              <span className="block text-xl font-bold text-[#1f2b45]">Crear JAM grupal</span>
              <span className="mt-1 block max-w-[17rem] text-sm leading-5 text-[#303244]">
                Invita a tus amigos, voten actividades y dividan gastos.
              </span>
            </span>
          </div>
          <span
            className={`flex h-10 w-16 items-center rounded-full p-1 transition-colors ${
              preferences.jamGroup ? 'justify-end bg-rojo-principal' : 'justify-start bg-gray-300'
            }`}
          >
            <span className="h-8 w-8 rounded-full bg-white shadow" />
          </span>
        </button>

        <button
          className="mt-10 w-full rounded-3xl bg-rojo-principal px-6 py-6 text-xl font-bold text-white shadow-lg hover-rojo"
          onClick={onNext}
        >
          Siguiente
        </button>
      </main>
    </div>
  )
}
