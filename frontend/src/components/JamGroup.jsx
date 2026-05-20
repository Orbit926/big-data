import {
  ArrowLeftIcon,
  UserPlusIcon,
  ChartIcon,
  WalletIcon,
  ChatIcon,
  MoneyIcon,
  ForkIcon,
  UmbrellaIcon,
  CheersIcon,
} from './Icons'
import ActionTile from './ActionTile'
import { formatSelectedRange } from '../utils/helpers'

function MiniOption({ label }) {
  return (
    <button className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white p-2 text-xs shadow-sm">
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-[#55b8cf] to-[#f4d29b] text-[10px] font-bold text-white">
        IMG
      </span>
      {label}
    </button>
  )
}

function ItineraryItem({ time, title, icon: Icon }) {
  return (
    <div className="grid grid-cols-[5.5rem_1.5rem_1fr_3.5rem] items-center border-b border-gray-100 px-4 py-3 last:border-b-0">
      <span className="font-bold text-rojo-principal">{time}</span>
      <span className="h-2.5 w-2.5 rounded-full bg-rojo-principal" />
      <span className="text-sm">{title}</span>
      <span className="grid h-10 w-10 place-items-center rounded-full bg-red-50 text-rojo-principal">
        <Icon className="h-6 w-6" />
      </span>
    </div>
  )
}

export default function JamGroup({ destination, selectedRange, travelers, onBack, onOpenExpenses, onNext }) {
  const dateLabel = formatSelectedRange(selectedRange)

  return (
    <div className="min-h-screen bg-white text-[#24304a]">
      <section className={`relative h-52 overflow-hidden bg-gradient-to-r ${destination.accent}`}>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white">
          <span className="text-5xl font-black tracking-[0.25em]">IMG</span>
          <span className="mt-3 text-sm font-semibold uppercase tracking-[0.2em] opacity-85">
            Espacio para imagen grupal
          </span>
        </div>
        <button
          className="absolute left-8 top-8 grid h-16 w-16 place-items-center rounded-full bg-white text-[#20222f] shadow-lg"
          aria-label="Volver"
          onClick={onBack}
        >
          <ArrowLeftIcon className="h-8 w-8" />
        </button>
      </section>

      <main className="relative -mt-7 rounded-t-[2.2rem] bg-white px-2 pb-5 pt-12">
        <h1 className="text-center text-4xl font-bold text-[#303244]">JAM grupal</h1>

        <section className="mt-14 rounded-2xl border border-gray-200 bg-white p-3 shadow-sm">
          <div className="flex items-center gap-5">
            <div className={`grid h-20 w-28 shrink-0 place-items-center overflow-hidden rounded-2xl bg-gradient-to-br ${destination.accent}`}>
              <span className="text-sm font-black tracking-[0.18em] text-white">{destination.emoji}</span>
            </div>
            <div className="min-w-0 flex-1 text-left">
              <h2 className="text-2xl font-bold text-[#24304a]">{destination.name}</h2>
              <p className="mt-1 text-base text-[#24304a]">
                {dateLabel} · {travelers} viajeros
              </p>
            </div>
            <span className="rounded-full bg-[#eaf7ef] px-4 py-2 text-sm font-medium text-[#3d936f]">
              Activo
            </span>
          </div>
        </section>

        <section className="mt-4 text-left">
          <h2 className="text-lg font-bold">Miembros ({travelers})</h2>
          <div className="mt-3 flex items-center gap-4">
            {Array.from({ length: Math.min(travelers, 4) }, (_, index) => (
              <div
                key={`member-${index}`}
                className="grid h-14 w-14 place-items-center rounded-full bg-[#e9eef7] text-sm font-bold text-rojo-principal"
              >
                IMG
              </div>
            ))}
            <button className="ml-auto flex h-14 items-center gap-2 rounded-2xl border border-gray-200 px-6 text-base font-medium text-[#24304a] shadow-sm">
              <UserPlusIcon className="h-7 w-7" />
              Invitar
            </button>
          </div>
        </section>

        <section className="mt-4 text-left">
          <h2 className="text-lg font-bold">Pendientes del grupo</h2>
          <div className="mt-3 grid grid-cols-2 gap-4">
            <div className="rounded-2xl border border-red-100 bg-red-50/30 p-4">
              <div className="flex items-center gap-4">
                <span className="grid h-14 w-14 place-items-center rounded-full bg-red-50 text-rojo-principal">
                  <ChartIcon className="h-8 w-8" />
                </span>
                <div>
                  <h3 className="font-bold">Votacion activa</h3>
                  <p className="text-sm">¿Que hacemos el sabado?</p>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <MiniOption label="Catamaran" />
                <MiniOption label="Xcaret" />
              </div>
              <button className="mt-4 w-full rounded-xl bg-rojo-principal py-3 font-bold text-white hover-rojo">
                Votar
              </button>
            </div>

            <button
              className="rounded-2xl border border-blue-100 bg-blue-50/20 p-4 text-left"
              onClick={onOpenExpenses}
            >
              <div className="flex items-center gap-4">
                <span className="grid h-14 w-14 place-items-center rounded-full bg-blue-50 text-[#3e73d8]">
                  <WalletIcon className="h-8 w-8" />
                </span>
                <div>
                  <h3 className="font-bold">Gastos grupales</h3>
                  <p className="text-sm">Ana pago el hotel</p>
                </div>
              </div>
              <div className="mt-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
                <p className="text-sm">Tu debes</p>
                <p className="mt-1 text-xl font-bold">$1,250 <span className="text-base font-medium">MXN</span></p>
              </div>
              <span className="mt-3 inline-flex rounded-full bg-blue-50 px-4 py-1 text-xs text-[#3e73d8]">
                Pendiente de liquidacion
              </span>
            </button>
          </div>
        </section>

        <section className="mt-4 text-left">
          <h2 className="text-lg font-bold">Itinerario de hoy</h2>
          <div className="mt-2 overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
            <ItineraryItem time="09:00" title="Desayuno en el hotel" icon={ForkIcon} />
            <ItineraryItem time="12:30" title="Playa Norte" icon={UmbrellaIcon} />
            <ItineraryItem time="20:00" title="Cena grupal" icon={CheersIcon} />
          </div>
        </section>

        <section className="mt-4 grid grid-cols-4 gap-3">
          <ActionTile label="Votar" icon={ChartIcon} />
          <ActionTile label="Agregar gasto" icon={MoneyIcon} />
          <ActionTile label="Invitar" icon={UserPlusIcon} />
          <ActionTile label="Chat" icon={ChatIcon} />
        </section>

        <button
          className="mt-4 w-full rounded-2xl bg-rojo-principal px-6 py-5 text-xl font-bold text-white shadow-lg hover-rojo"
          onClick={onNext}
        >
          Siguiente
        </button>
      </main>
    </div>
  )
}
