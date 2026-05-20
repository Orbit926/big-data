import {
  ArrowLeftIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  SparklesIcon,
  PlusCircleIcon,
  MapPinIcon,
  ShareIcon,
  ChatIcon,
  BriefcaseIcon,
  CalendarCheckIcon,
  SunIcon,
} from './Icons'
import ActionTile from './ActionTile'
import { formatSelectedRange } from '../utils/helpers'

function InfoStat({ icon: Icon, title, subtitle, tone }) {
  const tones = {
    blue: 'border-blue-100 bg-blue-50/30 text-[#3e73d8]',
    green: 'border-green-100 bg-green-50/40 text-[#3d936f]',
    yellow: 'border-yellow-100 bg-yellow-50/60 text-[#e7a926]',
  }

  return (
    <div className={`rounded-2xl border p-3 ${tones[tone]}`}>
      <div className="flex items-center gap-3">
        <span className="grid h-11 w-11 place-items-center rounded-full bg-white/70">
          <Icon className="h-7 w-7" />
        </span>
        <div className="text-left">
          <p className="font-bold text-[#24304a]">{title}</p>
          <p className="text-sm text-[#24304a]">{subtitle}</p>
        </div>
      </div>
    </div>
  )
}

function PlanRow({ plan }) {
  return (
    <article
      className={`relative grid grid-cols-[4.5rem_1fr] gap-3 border-l border-dashed border-gray-200 pb-3 pl-4 ${
        plan.featured ? 'rounded-2xl border border-red-200 bg-red-50/20 p-3 pl-4' : ''
      }`}
    >
      <div className="absolute -left-1.5 top-5 h-3 w-3 rounded-full bg-rojo-principal" />
      <time className="pt-3 font-bold text-rojo-principal">{plan.time}</time>
      <div className="rounded-2xl border border-gray-100 bg-white p-3 shadow-sm">
        <div className="flex gap-4">
          <div className={`grid h-16 w-20 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${plan.featured ? 'from-[#6abbe7] to-[#dcefff]' : 'from-[#92d0e3] to-[#f4c88b]'}`}>
            <span className="text-xs font-bold text-white">IMG</span>
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-lg font-bold">{plan.title}</h3>
              {plan.featured && (
                <span className="rounded-full bg-purple-50 px-3 py-1 text-xs text-[#6148bd]">
                  Destacado
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500">{plan.description}</p>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-[#24304a]">
              <span>{plan.place}</span>
              <span>{plan.duration}</span>
              <span className="flex items-center gap-1">
                <span className="inline-flex -space-x-1">
                  <span className="h-5 w-5 rounded-full bg-[#e9eef7]" />
                  <span className="h-5 w-5 rounded-full bg-[#d7e3f7]" />
                  <span className="h-5 w-5 rounded-full bg-[#e9d8c8]" />
                </span>
                {plan.people}
              </span>
            </div>
          </div>
          <div className="flex items-center">
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                plan.status === 'Planeado' ? 'bg-blue-50 text-[#3e73d8]' : 'bg-green-50 text-[#3d936f]'
              }`}
            >
              {plan.status}
            </span>
          </div>
        </div>
      </div>
    </article>
  )
}

export default function TripItinerary({ destination, selectedRange, travelers, onBack }) {
  const dateLabel = formatSelectedRange(selectedRange)
  const dayTabs = [
    { day: 'Dia 1', date: 'Vie 6 Feb' },
    { day: 'Dia 2', date: 'Sab 7 Feb' },
    { day: 'Dia 3', date: 'Sab 8 Feb', active: true },
    { day: 'Dia 4', date: 'Dom 9 Feb' },
    { day: 'Dia 5', date: 'Lun 10 Feb' },
  ]
  const plans = [
    {
      time: '09:00',
      title: 'Desayuno frente al mar',
      description: 'Disfruta de la vista y buena compania.',
      place: 'Hotel Zone',
      duration: '1 h',
      people: '4 van',
      status: 'Listo',
    },
    {
      time: '11:30',
      title: 'Playa Norte',
      description: 'Tarde libre de playa y descanso.',
      place: 'Isla Mujeres',
      duration: '2 h',
      people: '3 van',
      status: 'Planeado',
    },
    {
      time: '15:00',
      title: 'Catamaran',
      description: 'Paseo de 3 h con bebidas y snorkel.',
      place: 'Mar Caribe',
      duration: '3 h',
      people: '4 van',
      status: 'Reservado',
      featured: true,
    },
    {
      time: '20:00',
      title: 'Cena grupal',
      description: 'Cerramos el dia con buena comida.',
      place: 'Downtown Cancun',
      duration: '2 h',
      people: '4 van',
      status: 'Planeado',
    },
  ]

  return (
    <div className="min-h-screen bg-white text-[#24304a]">
      <section className={`relative h-52 overflow-hidden bg-gradient-to-r ${destination.accent}`}>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white">
          <span className="text-5xl font-black tracking-[0.25em]">IMG</span>
          <span className="mt-3 text-sm font-semibold uppercase tracking-[0.2em] opacity-85">
            Espacio para imagen de itinerario
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

      <main className="relative -mt-7 rounded-t-[2.2rem] bg-white px-3 pb-8 pt-12">
        <h1 className="text-center text-4xl font-bold text-[#303244]">Itinerario</h1>

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

        <section className="mt-4 flex items-center gap-3 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <button className="shrink-0 text-2xl text-gray-400" aria-label="Dia anterior">
            <ChevronLeftIcon className="h-6 w-6" />
          </button>
          {dayTabs.map((tab) => (
            <button
              key={tab.day}
              className={`min-w-[5.5rem] rounded-2xl border px-3 py-3 text-center shadow-sm ${
                tab.active
                  ? 'border-rojo-principal bg-rojo-principal text-white'
                  : 'border-gray-200 bg-white text-[#24304a]'
              }`}
            >
              <span className="block font-bold">{tab.day}</span>
              <span className="mt-1 block text-xs">{tab.date}</span>
            </button>
          ))}
          <button className="shrink-0 text-2xl text-gray-400" aria-label="Dia siguiente">
            <ChevronRightIcon className="h-6 w-6" />
          </button>
        </section>

        <section className="mt-4 grid grid-cols-3 gap-3">
          <InfoStat icon={BriefcaseIcon} title="5 planes" subtitle="para hoy" tone="blue" />
          <InfoStat icon={CalendarCheckIcon} title="2 reservas" subtitle="confirmadas" tone="green" />
          <InfoStat icon={SunIcon} title="Clima" subtitle="28° Soleado" tone="yellow" />
        </section>

        <section className="mt-5 text-left">
          <h2 className="text-2xl font-bold">Dia 3 - Sabado</h2>
          <div className="mt-4">
            {plans.map((plan) => (
              <PlanRow key={`${plan.time}-${plan.title}`} plan={plan} />
            ))}
          </div>
        </section>

        <section className="mt-4 flex overflow-hidden rounded-2xl border border-purple-100 bg-purple-50/60 pl-5 text-left">
          <div className="flex flex-1 items-center gap-4 py-4">
            <SparklesIcon className="h-12 w-12 shrink-0 text-[#6148bd]" />
            <div>
              <h3 className="font-bold text-[#3d2d91]">MOVE AI</h3>
              <p className="mt-1 text-sm text-[#3d2d91]">
                Te recomendamos salir a Playa Norte antes del catamaran para aprovechar mejor el dia.
              </p>
            </div>
          </div>
          <div className="grid w-28 place-items-center text-rojo-principal">
            <span className="text-xl font-black">IMG</span>
          </div>
        </section>

        <section className="mt-4 grid grid-cols-4 gap-3">
          <ActionTile label="Agregar plan" icon={PlusCircleIcon} />
          <ActionTile label="Mapa" icon={MapPinIcon} />
          <ActionTile label="Compartir" icon={ShareIcon} />
          <ActionTile label="Chat" icon={ChatIcon} />
        </section>

        <button className="mt-4 w-full rounded-2xl bg-rojo-principal px-6 py-5 text-xl font-bold text-white shadow-lg hover-rojo">
          Ver itinerario completo
        </button>
      </main>
    </div>
  )
}
