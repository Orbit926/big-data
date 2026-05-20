import { ArrowLeftIcon, BookmarkIcon, StarIcon } from './Icons'

export default function DestinationDetails({ destination, onBack, onStartTrip }) {
  return (
    <div className="min-h-screen bg-white text-[#20222f]">
      <section className={`relative min-h-[46vh] overflow-hidden bg-gradient-to-br ${destination.accent}`}>
        {destination.image ? (
          <img
            src={destination.image}
            alt={destination.name}
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center px-8 text-center text-white">
            <span className="text-6xl font-black tracking-[0.25em]">{destination.emoji}</span>
            <span className="mt-4 text-sm font-semibold uppercase tracking-[0.2em] opacity-85">
              Espacio para imagen principal
            </span>
          </div>
        )}

        <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between px-6 pt-8 text-white">
          <button
            className="grid h-16 w-16 place-items-center rounded-full bg-white/25 backdrop-blur"
            aria-label="Volver"
            onClick={onBack}
          >
            <ArrowLeftIcon className="h-8 w-8" />
          </button>
          <h1 className="text-2xl font-bold drop-shadow">Detalles</h1>
          <button
            className="grid h-12 w-12 place-items-center rounded-2xl bg-black/15 backdrop-blur"
            aria-label={`Guardar ${destination.name}`}
          >
            <BookmarkIcon className="h-7 w-7" />
          </button>
        </div>
      </section>

      <section className="relative -mt-10 rounded-t-[2.2rem] bg-white px-8 pb-8 pt-6 text-left">
        <div className="mx-auto mb-8 h-1.5 w-14 rounded-full bg-gray-200" />

        <div className="flex items-start justify-between gap-5">
          <div>
            <h2 className="text-4xl font-semibold leading-tight text-[#20222f]">{destination.name}</h2>
            <p className="mt-3 text-2xl text-gray-500">{destination.country}</p>
          </div>
          <div className="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-full bg-[#c9f2cd] text-sm font-bold text-[#ef4b49]">
            IMG
          </div>
        </div>

        <div className="mt-9 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xl">
            <StarIcon className="h-7 w-7 text-[#ffc94c]" />
            <span className="font-semibold">{destination.rating}</span>
            <span className="text-gray-500">({destination.reviews})</span>
          </div>
          <p className="text-xl font-medium text-[#1b66ff]">{destination.price}</p>
        </div>

        <div className="mt-9 flex gap-7 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {destination.gallery.map((image, index) => (
            <div
              key={`${destination.id}-gallery-${index}`}
              className={`relative h-16 w-16 shrink-0 overflow-hidden rounded-2xl bg-gradient-to-br ${destination.accent}`}
            >
              {image ? (
                <img
                  src={image}
                  alt={`${destination.name} ${index + 1}`}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="grid h-full w-full place-items-center text-xs font-bold text-white">
                  IMG
                </div>
              )}
              {index === destination.gallery.length - 1 && (
                <div className="absolute inset-0 grid place-items-center bg-black/35 text-sm font-bold text-white">
                  +16
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-9">
          <h3 className="text-3xl font-bold text-[#20222f]">Sobre este viaje</h3>
          <p className="mt-5 max-w-xl text-xl leading-9 text-gray-500">
            {destination.description}
          </p>
        </div>

        <button
          className="mt-12 w-full rounded-3xl bg-rojo-principal px-6 py-6 text-xl font-bold text-white shadow-lg hover-rojo"
          onClick={onStartTrip}
        >
          Comenzar viaje
        </button>
      </section>
    </div>
  )
}
