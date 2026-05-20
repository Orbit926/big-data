import { BookmarkIcon, PinIcon, StarIcon } from './Icons'

export default function DestinationCard({ destination, onSelect }) {
  return (
    <article
      className="w-[76vw] max-w-[380px] shrink-0 snap-start rounded-[2rem] bg-white p-4 text-left shadow-[0_18px_45px_rgba(22,30,46,0.08)]"
      onClick={() => onSelect(destination)}
      role="button"
      tabIndex="0"
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onSelect(destination)
        }
      }}
    >
      <div className={`relative aspect-square overflow-hidden rounded-[1.7rem] bg-gradient-to-b ${destination.accent}`}>
        {destination.image ? (
          <img
            src={destination.image}
            alt={destination.name}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full flex-col items-center justify-center px-6 text-center text-white">
            <span className="text-5xl font-black tracking-[0.25em]">{destination.emoji}</span>
            <span className="mt-4 max-w-[12rem] text-sm font-semibold uppercase tracking-[0.18em] opacity-85">
              Espacio para imagen
            </span>
          </div>
        )}
        <button
          className="absolute right-5 top-5 grid h-11 w-11 place-items-center rounded-2xl bg-black/20 text-white backdrop-blur"
          aria-label={`Guardar ${destination.name}`}
          onClick={(event) => event.stopPropagation()}
        >
          <BookmarkIcon className="h-6 w-6" />
        </button>
      </div>

      <div className="flex items-start justify-between px-2 pt-5">
        <div>
          <h3 className="text-2xl font-semibold text-[#20222f]">{destination.name}</h3>
          <p className="mt-3 flex items-center gap-2 text-xl text-gray-500">
            <PinIcon className="h-6 w-6" />
            {destination.country}
          </p>
        </div>
        <div className="flex items-center gap-1 pt-1 text-xl font-semibold text-[#20222f]">
          <StarIcon className="h-6 w-6 text-[#ffc94c]" />
          {destination.rating}
        </div>
      </div>
    </article>
  )
}
