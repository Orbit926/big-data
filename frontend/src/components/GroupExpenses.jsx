import {
  ArrowLeftIcon,
  WalletIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  ChevronRightIcon,
  BuildingIcon,
  BusIcon,
  ForkIcon,
  SailboatIcon,
  MoneyIcon,
  PercentIcon,
  BellIcon,
  ClockIcon,
} from './Icons'
import ActionTile from './ActionTile'
import { formatSelectedRange } from '../utils/helpers'

function ExpenseMetric({ title, amount, color, icon: Icon }) {
  const colorClasses = {
    blue: 'border-blue-100 bg-blue-50/30 text-[#3e73d8]',
    green: 'border-green-100 bg-green-50/40 text-[#3d936f]',
    red: 'border-red-100 bg-red-50/40 text-rojo-principal',
  }

  return (
    <div className={`rounded-2xl border p-3 ${colorClasses[color]}`}>
      <div className="flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-full bg-white/70">
          <Icon className="h-6 w-6" />
        </span>
        <div className="text-left">
          <p className="text-sm font-semibold text-[#24304a]">{title}</p>
          <p className="mt-1 text-xl font-bold text-[#24304a]">
            {amount} <span className="text-xs font-medium">MXN</span>
          </p>
        </div>
      </div>
    </div>
  )
}

function BalanceRow({ person, index }) {
  return (
    <div className="flex items-center gap-3 border-b border-gray-100 px-3 py-2 last:border-b-0">
      <div className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-[#e9eef7] text-xs font-bold text-rojo-principal">
        IMG
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="font-bold">{person.name}</h3>
        <p className="text-sm text-gray-500">{person.detail}</p>
      </div>
      <span
        className={`rounded-full px-3 py-1 text-xs font-medium ${
          person.positive ? 'bg-green-50 text-[#3d936f]' : 'bg-red-50 text-rojo-principal'
        }`}
      >
        {person.status} {person.amount}
      </span>
      <ChevronRightIcon className="h-5 w-5 text-gray-400" />
      <span className="sr-only">Persona {index + 1}</span>
    </div>
  )
}

function MovementRow({ movement }) {
  const Icon = movement.icon

  return (
    <div className="flex items-center gap-3 border-b border-gray-100 px-3 py-3 last:border-b-0">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-red-50 text-rojo-principal">
        <Icon className="h-6 w-6" />
      </span>
      <div className="min-w-0 flex-1">
        <h3 className="text-sm font-bold">{movement.title}</h3>
        <p className="text-xs text-gray-500">{movement.detail}</p>
      </div>
      <span className="font-bold">{movement.amount}</span>
    </div>
  )
}

function SettlementRow({ settlement }) {
  return (
    <div className="grid grid-cols-[1fr_1.5rem_1fr_4rem] items-center gap-2 border-b border-gray-100 py-3 last:border-b-0">
      <PersonChip name={settlement.from} />
      <span className="text-center text-rojo-principal">-&gt;</span>
      <PersonChip name={settlement.to} />
      <span className="text-right text-sm font-bold text-rojo-principal">
        {settlement.amount}
        <span className="block text-xs font-medium text-gray-500">MXN</span>
      </span>
    </div>
  )
}

function PersonChip({ name }) {
  return (
    <span className="flex items-center gap-2 text-xs">
      <span className="grid h-8 w-8 place-items-center rounded-full bg-[#e9eef7] text-[10px] font-bold text-rojo-principal">
        IMG
      </span>
      {name}
    </span>
  )
}

export default function GroupExpenses({ destination, selectedRange, travelers, onBack }) {
  const dateLabel = formatSelectedRange(selectedRange)
  const balances = [
    { name: 'Ana', detail: 'Pago $3,500', status: 'A favor', amount: '+$1,340', positive: true },
    { name: 'Gabriel', detail: 'Debe $1,250', status: 'Pendiente', amount: '', positive: false },
    { name: 'Santiago', detail: 'Pago $1,400', status: 'A favor', amount: '+$240', positive: true },
    { name: 'Tenoch', detail: 'Debe $1,190', status: 'Pendiente', amount: '', positive: false },
  ]
  const movements = [
    { title: 'Ana pago el hotel', detail: 'Para 4 viajeros', amount: '$4,000', icon: BuildingIcon },
    { title: 'Santiago pago transporte', detail: 'Aeropuerto - hotel', amount: '$640', icon: BusIcon },
    { title: 'Tenoch pago cena grupal', detail: 'Restaurante frente al mar', amount: '$1,200', icon: ForkIcon },
    { title: 'Gabriel pago boletos', detail: 'Tour en catamaran', amount: '$2,800', icon: SailboatIcon },
  ]
  const settlements = [
    { from: 'Gabriel', to: 'Ana', amount: '$1,250' },
    { from: 'Tenoch', to: 'Ana', amount: '$90' },
    { from: 'Tenoch', to: 'Santiago', amount: '$1,100' },
  ]

  return (
    <div className="min-h-screen bg-white text-[#24304a]">
      <section className={`relative h-52 overflow-hidden bg-gradient-to-r ${destination.accent}`}>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white">
          <span className="text-5xl font-black tracking-[0.25em]">IMG</span>
          <span className="mt-3 text-sm font-semibold uppercase tracking-[0.2em] opacity-85">
            Espacio para imagen de gastos
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

      <main className="relative -mt-7 rounded-t-[2.2rem] bg-white px-5 pb-8 pt-12">
        <h1 className="text-center text-4xl font-bold text-[#303244]">Gastos Grupales</h1>

        <section className="mt-8 rounded-2xl border border-gray-200 bg-white p-3 shadow-sm">
          <div className="flex items-center gap-4">
            <div className={`grid h-16 w-24 shrink-0 place-items-center overflow-hidden rounded-xl bg-gradient-to-br ${destination.accent}`}>
              <span className="text-xs font-black tracking-[0.16em] text-white">{destination.emoji}</span>
            </div>
            <div className="min-w-0 flex-1 text-left">
              <h2 className="text-2xl font-bold text-[#24304a]">{destination.name}</h2>
              <p className="mt-1 text-sm text-[#24304a]">
                {dateLabel} - {travelers} viajeros
              </p>
            </div>
            <span className="rounded-full bg-[#eaf7ef] px-4 py-2 text-sm font-medium text-[#3d936f]">
              Activo
            </span>
          </div>
        </section>

        <section className="mt-4 grid grid-cols-3 gap-3">
          <ExpenseMetric title="Total del viaje" amount="$8,640" color="blue" icon={WalletIcon} />
          <ExpenseMetric title="Pagado" amount="$6,200" color="green" icon={CheckCircleIcon} />
          <ExpenseMetric title="Pendiente" amount="$2,440" color="red" icon={AlertCircleIcon} />
        </section>

        <section className="mt-4 text-left">
          <h2 className="text-lg font-bold">Balance por persona</h2>
          <div className="mt-2 overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
            {balances.map((person, index) => (
              <BalanceRow key={person.name} person={person} index={index} />
            ))}
          </div>
        </section>

        <section className="mt-4 grid grid-cols-2 gap-4 text-left">
          <div>
            <h2 className="text-lg font-bold">Movimientos recientes</h2>
            <div className="mt-2 overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
              {movements.map((movement) => (
                <MovementRow key={movement.title} movement={movement} />
              ))}
              <button className="flex w-full items-center justify-center gap-2 border-t border-gray-100 py-3 text-sm font-medium text-[#1b66ff]">
                Ver todos los movimientos
                <ChevronRightIcon className="h-5 w-5" />
              </button>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold">Liquidacion</h2>
            <div className="mt-2 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
              <p className="mb-4 text-sm leading-5">
                Para que todos queden en ceros, realiza los siguientes pagos:
              </p>
              {settlements.map((settlement) => (
                <SettlementRow key={`${settlement.from}-${settlement.to}-${settlement.amount}`} settlement={settlement} />
              ))}
            </div>
          </div>
        </section>

        <section className="mt-4 grid grid-cols-4 gap-3">
          <ActionTile label="Agregar gasto" icon={MoneyIcon} />
          <ActionTile label="Dividir" icon={PercentIcon} />
          <ActionTile label="Recordar" icon={BellIcon} />
          <ActionTile label="Historial" icon={ClockIcon} />
        </section>

        <button className="mt-4 w-full rounded-2xl bg-rojo-principal px-6 py-5 text-xl font-bold text-white shadow-lg hover-rojo">
          Liquidar ahora
        </button>
      </main>
    </div>
  )
}
