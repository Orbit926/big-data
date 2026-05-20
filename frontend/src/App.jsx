import { useState, useEffect } from 'react'

const fallbackDestinationsInfo = [
  {
    id: 1,
    name: 'Paris',
    country: 'Francia',
    rating: '4.7',
    reviews: '2.4k',
    price: 'Desde $3,899 MXN',
    description: 'Disfruta calles historicas, cafes encantadores, museos y planes perfectos para viajar con amigos o en grupo.',
    image: '',
    gallery: ['', '', '', '', ''],
    accent: 'from-[#193457] via-[#44a8d4] to-[#f7c66a]',
    emoji: 'PAR',
  },
  {
    id: 2,
    name: 'New York',
    country: 'Estados Unidos',
    rating: '4.8',
    reviews: '4.1k',
    price: 'Desde $5,299 MXN',
    description: 'Explora rascacielos, parques, miradores, compras y noches llenas de energia para compartir con tus amigos.',
    image: '',
    gallery: ['', '', '', '', ''],
    accent: 'from-[#202634] via-[#5f8fd9] to-[#f2d27a]',
    emoji: 'NYC',
  },
  {
    id: 3,
    name: 'Mexico',
    country: 'Mexico',
    rating: '4.6',
    reviews: '3.1k',
    price: 'Desde $2,499 MXN',
    description: 'Disfruta playas increibles, comida, cultura, experiencias acuaticas y planes perfectos para viajar con amigos o en grupo.',
    image: '',
    gallery: ['', '', '', '', ''],
    accent: 'from-[#167c5b] via-[#f0b64f] to-[#de5f45]',
    emoji: 'MEX',
  },
]

const navItems = [
  { id: 'home', label: 'Inicio', icon: HomeIcon },
  { id: 'itinerary', label: 'Itinerario', icon: CalendarIcon },
  { id: 'jams', label: 'JAMs', icon: ChatIcon },
  { id: 'profile', label: 'Perfil', icon: UserIcon },
]

const monthNames = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
]

const weekDays = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do']

const travelCompanions = ['Solo', 'Pareja', 'Amigos', 'Familia', 'Trabajo']
const budgetOptions = ['Economico', 'Moderado', 'Comodo', 'Premium']
const travelStyles = ['Relax', 'Aventura', 'Fiesta', 'Cultural', 'Comida']

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordReg, setShowPasswordReg] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')
  const [currentUser, setCurrentUser] = useState('Leonardo')
  const [currentNavTab, setCurrentNavTab] = useState('home')
  const [destinations, setDestinations] = useState(fallbackDestinationsInfo)
  const [selectedDestination, setSelectedDestination] = useState(fallbackDestinationsInfo[0])
  const [calendarDate, setCalendarDate] = useState(new Date(2027, 1, 1))

  useEffect(() => {
    fetch('/api/search/destinations/')
      .then(res => res.json())
      .then(data => {
        if (!Array.isArray(data)) return
        const mapped = data.map((d, i) => {
          const fallback = fallbackDestinationsInfo[i % fallbackDestinationsInfo.length]
          return {
            ...fallback,
            id: d.id,
            name: d.name,
            country: d.country,
            description: d.description,
            price: d.avg_cost_per_day ? `Desde $${d.avg_cost_per_day} MXN` : fallback.price
          }
        })
        if (mapped.length > 0) {
          setDestinations(mapped)
          setSelectedDestination(mapped[0])
        }
      })
      .catch(e => console.error("Error fetching destinations:", e))
  }, [])

  const [selectedRange, setSelectedRange] = useState({ start: null, end: null })
  const [tripPreferences, setTripPreferences] = useState({
    companion: 'Amigos',
    travelers: 4,
    budget: 'Moderado',
    style: 'Fiesta',
    jamGroup: true,
  })

  const goToDashboard = (userName) => {
    setCurrentUser(userName || 'Leonardo')
    setCurrentPage('dashboard')
    setCurrentNavTab('home')
  }

  const openDestination = (destination) => {
    setSelectedDestination(destination)
    setCurrentPage('details')
  }

  if (currentPage === 'home') {
    return (
      <AuthShell>
        <div className="text-center mb-12 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold text-azul-oscuro mb-2">
            Tu mejor aventura
          </h1>
          <p className="text-4xl md:text-5xl font-bold text-turquesa">
            comienza aqui
          </p>
        </div>

        <div className="mb-12 flex justify-center w-full max-w-md">
          <div className="relative w-full aspect-square max-w-sm rounded-full overflow-hidden bg-white shadow-xl flex items-center justify-center">
            <img
              src="/img/Fox_signin-reg.png"
              alt="Tu aventura comienza aqui"
              className="w-full h-full object-cover"
            />
          </div>
        </div>

        <div className="w-full max-w-md space-y-4">
          <button
            className="w-full bg-rojo-principal hover-rojo text-white font-bold text-xl py-4 px-6 rounded-full shadow-lg transition-colors duration-300"
            onClick={() => setCurrentPage('login')}
          >
            Iniciar Sesion
          </button>
          <button
            className="w-full bg-white text-rojo-principal font-bold text-xl py-4 px-6 rounded-full shadow-lg transition-colors duration-300 hover:bg-gray-50"
            onClick={() => setCurrentPage('register')}
          >
            Registrarse
          </button>
        </div>
      </AuthShell>
    )
  }

  if (currentPage === 'login') {
    return (
      <AuthShell onBack={() => setCurrentPage('home')}>
        <div className="text-center mb-8 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold text-azul-oscuro mb-2">
            Bienvenido de vuelta
          </h1>
          <p className="text-lg text-gray-500">
            Inicia sesion y continua tu proxima aventura
          </p>
        </div>

        <div className="w-full max-w-md space-y-4">
          <input
            type="email"
            placeholder="www.uihut@gmail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-6 py-4 bg-white rounded-lg border-0 text-azul-oscuro placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rojo-principal"
          />

          <PasswordField
            value={password}
            showPassword={showPassword}
            onChange={setPassword}
            onToggle={() => setShowPassword(!showPassword)}
          />

          <div className="text-right">
            <a href="#" className="text-blue-500 font-semibold hover:text-blue-600 transition-colors">
              Olvide mi contrasena
            </a>
          </div>

          <button
            className="w-full bg-rojo-principal hover-rojo text-white font-bold text-xl py-4 px-6 rounded-full shadow-lg transition-colors duration-300 mt-8"
            onClick={() => goToDashboard(email)}
          >
            Iniciar Sesion
          </button>
        </div>
      </AuthShell>
    )
  }

  if (currentPage === 'register') {
    return (
      <AuthShell onBack={() => setCurrentPage('home')}>
        <div className="text-center mb-8 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold text-azul-oscuro mb-2">
            Crea tu cuenta
          </h1>
          <p className="text-lg text-gray-500">
            Empieza a planear viajes increibles con MOVE
          </p>
        </div>

        <div className="w-full max-w-md space-y-4">
          <input
            type="text"
            placeholder="Leonardo Smith"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-6 py-4 bg-white rounded-lg border-0 text-azul-oscuro placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rojo-principal"
          />

          <input
            type="email"
            placeholder="www.uihut@gmail.com"
            value={regEmail}
            onChange={(e) => setRegEmail(e.target.value)}
            className="w-full px-6 py-4 bg-white rounded-lg border-0 text-azul-oscuro placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-rojo-principal"
          />

          <PasswordField
            value={regPassword}
            showPassword={showPasswordReg}
            onChange={setRegPassword}
            onToggle={() => setShowPasswordReg(!showPasswordReg)}
          />

          <button
            className="w-full bg-rojo-principal hover-rojo text-white font-bold text-xl py-4 px-6 rounded-full shadow-lg transition-colors duration-300 mt-8"
            onClick={() => goToDashboard(name)}
          >
            Registrarse
          </button>
        </div>
      </AuthShell>
    )
  }

  if (currentPage === 'dashboard') {
    return (
      <div className="min-h-screen bg-white text-[#20222f]">
        <main className="min-h-screen pb-28">
          {currentNavTab === 'search' ? (
            <HotelSearch />
          ) : (
            <>
              <header className="flex items-center justify-between px-6 pt-5">
                <button className="flex items-center gap-3 rounded-full bg-[#f6f6f8] py-2 pl-2 pr-6">
                  <span className="grid h-12 w-12 place-items-center overflow-hidden rounded-full bg-[#e8eefc]">
                    <span className="text-sm font-bold text-[#ef4b49]">IMG</span>
                  </span>
                  <span className="text-lg font-semibold">{currentUser || 'Leonardo'}</span>
                </button>
                <button
                  className="relative grid h-16 w-16 place-items-center rounded-full bg-[#f8f8fa]"
                  aria-label="Notificaciones"
                >
                  <BellIcon className="h-8 w-8" />
                  <span className="absolute right-5 top-5 h-2.5 w-2.5 rounded-full bg-rojo-principal" />
                </button>
              </header>

              <section className="px-6 pt-10 text-left">
                <h1 className="max-w-sm text-[3.25rem] font-light leading-[1.08] text-[#353844] sm:text-6xl">
                  Descubre tu
                  <span className="block font-bold text-[#1d202b]">
                    proximo <span className="text-[#58bcae]">viaje!</span>
                  </span>
                </h1>
                <div className="ml-56 mt-1 h-3 w-36 rounded-[50%] border-t-4 border-[#58bcae]" />
              </section>

              <section className="mt-8">
                <div className="mb-6 flex items-center justify-between px-6">
                  <h2 className="text-2xl font-bold text-[#20222f]">Para ir con tus amigos</h2>
                  <button className="text-lg font-medium text-rojo-principal">Ver todo</button>
                </div>

                <div className="flex snap-x snap-mandatory gap-6 overflow-x-auto px-6 pb-5 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                  {destinations.map((destination) => (
                    <DestinationCard
                      key={destination.id}
                      destination={destination}
                      onSelect={openDestination}
                    />
                  ))}
                </div>
              </section>
            </>
          )}
        </main>

        <BottomNav currentNavTab={currentNavTab} setCurrentNavTab={setCurrentNavTab} />
      </div>
    )
  }

  if (currentPage === 'details') {
    return (
      <DestinationDetails
        destination={selectedDestination}
        onBack={() => setCurrentPage('dashboard')}
        onStartTrip={() => setCurrentPage('date')}
      />
    )
  }

  if (currentPage === 'date') {
    return (
      <DateSelection
        calendarDate={calendarDate}
        selectedRange={selectedRange}
        setSelectedRange={setSelectedRange}
        onBack={() => setCurrentPage('details')}
        onMonthChange={setCalendarDate}
        onNext={() => setCurrentPage('preferences')}
      />
    )
  }

  if (currentPage === 'preferences') {
    return (
      <TripPreferences
        preferences={tripPreferences}
        setPreferences={setTripPreferences}
        onBack={() => setCurrentPage('date')}
        onNext={() => setCurrentPage('jam')}
      />
    )
  }

  if (currentPage === 'jam') {
    return (
      <JamGroup
        destination={selectedDestination}
        selectedRange={selectedRange}
        travelers={tripPreferences.travelers}
        onBack={() => setCurrentPage('preferences')}
        onOpenExpenses={() => setCurrentPage('expenses')}
        onNext={() => setCurrentPage('itinerary')}
      />
    )
  }

  if (currentPage === 'expenses') {
    return (
      <GroupExpenses
        destination={selectedDestination}
        selectedRange={selectedRange}
        travelers={tripPreferences.travelers}
        onBack={() => setCurrentPage('jam')}
      />
    )
  }

  if (currentPage === 'itinerary') {
    return (
      <TripItinerary
        destination={selectedDestination}
        selectedRange={selectedRange}
        travelers={tripPreferences.travelers}
        onBack={() => setCurrentPage('jam')}
      />
    )
  }

  return null
}

function HotelSearch() {
  const [query, setQuery] = useState('')
  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ next: null, previous: null })

  const fetchHotels = (url) => {
    setLoading(true)
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setHotels(data.results || [])
        setPagination({ next: data.next, previous: data.previous })
      })
      .catch(e => console.error("Error fetching hotels:", e))
      .finally(() => setLoading(false))
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (!query) return
    fetchHotels(`/api/search/hotels/?q=${encodeURIComponent(query)}`)
  }

  return (
    <div className="px-6 pt-10 text-left">
      <h1 className="text-3xl font-bold text-[#20222f] mb-6">Encuentra el hotel ideal</h1>
      <form onSubmit={handleSearch} className="mb-8 relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Busca por ciudad o nombre..."
          className="w-full bg-[#f6f6f8] text-[#20222f] px-6 py-4 rounded-full outline-none focus:ring-2 focus:ring-rojo-principal text-lg placeholder-gray-400"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-rojo-principal text-white p-3 rounded-full hover-rojo transition-colors"
          disabled={loading}
        >
          <SearchIcon className="h-6 w-6" />
        </button>
      </form>

      {loading ? (
        <div className="flex justify-center items-center py-20 text-rojo-principal text-xl font-bold">
          Cargando...
        </div>
      ) : (
        <>
          <div className="space-y-6">
            {hotels.map(hotel => (
              <div key={hotel.id} className="bg-white rounded-[2rem] shadow-[0_18px_45px_rgba(22,30,46,0.08)] overflow-hidden">
                <div className="h-48 bg-gradient-to-br from-[#202634] via-[#5f8fd9] to-[#f2d27a] relative">
                  {hotel.image_url && <img src={hotel.image_url} alt={hotel.name} className="w-full h-full object-cover" />}
                  <div className="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1">
                    <StarIcon className="h-4 w-4 text-[#ffc94c]" /> {hotel.rating}
                  </div>
                </div>
                <div className="p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-[#20222f] leading-tight">{hotel.name}</h3>
                    <div className="text-right shrink-0 ml-4">
                      <span className="block text-xl font-bold text-[#1b66ff]">${hotel.price_per_night}</span>
                      <span className="block text-xs text-gray-500 uppercase">{hotel.currency} / noche</span>
                    </div>
                  </div>
                  <p className="flex items-center gap-1 text-sm text-gray-500 mb-4">
                    <PinIcon className="h-4 w-4" /> {hotel.city}, {hotel.country}
                  </p>
                  <p className="text-sm text-gray-600 line-clamp-2 mb-4">{hotel.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {hotel.tags?.slice(0, 3).map(tag => (
                      <span key={tag} className="bg-[#f6f6f8] text-xs font-semibold px-3 py-1 rounded-full text-gray-600">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {(pagination.previous || pagination.next) && (
            <div className="flex justify-between mt-8 mb-4">
              <button
                disabled={!pagination.previous}
                onClick={() => fetchHotels(pagination.previous)}
                className="bg-[#f6f6f8] disabled:opacity-50 text-[#20222f] px-6 py-3 rounded-full font-bold shadow hover:bg-gray-200 transition"
              >
                Anterior
              </button>
              <button
                disabled={!pagination.next}
                onClick={() => fetchHotels(pagination.next)}
                className="bg-rojo-principal disabled:opacity-50 text-white px-6 py-3 rounded-full font-bold shadow-lg hover-rojo transition"
              >
                Siguiente
              </button>
            </div>
          )}
          
          {!loading && hotels.length === 0 && query && (
            <div className="text-center py-10 text-gray-500 text-lg">
              No se encontraron hoteles para tu búsqueda.
            </div>
          )}
        </>
      )}
    </div>
  )
}

function AuthShell({ children, onBack }) {
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

function PasswordField({ value, showPassword, onChange, onToggle }) {
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

function DestinationCard({ destination, onSelect }) {
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

function DestinationDetails({ destination, onBack, onStartTrip }) {
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

function DateSelection({
  calendarDate,
  selectedRange,
  setSelectedRange,
  onBack,
  onMonthChange,
  onNext,
}) {
  const year = calendarDate.getFullYear()
  const month = calendarDate.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDay = new Date(year, month, 1).getDay()
  const leadingSpaces = firstDay === 0 ? 6 : firstDay - 1
  const calendarCells = [
    ...Array.from({ length: leadingSpaces }, () => null),
    ...Array.from({ length: daysInMonth }, (_, index) => index + 1),
  ]

  const changeMonth = (step) => {
    onMonthChange(new Date(year, month + step, 1))
    setSelectedRange({ start: null, end: null })
  }

  const selectRangeDay = (day) => {
    if (!selectedRange.start || selectedRange.end) {
      setSelectedRange({ start: day, end: null })
      return
    }

    if (day < selectedRange.start) {
      setSelectedRange({ start: day, end: selectedRange.start })
      return
    }

    setSelectedRange({ start: selectedRange.start, end: day })
  }

  const isDaySelected = (day) => {
    if (!selectedRange.start) {
      return false
    }

    if (!selectedRange.end) {
      return day === selectedRange.start
    }

    return day >= selectedRange.start && day <= selectedRange.end
  }

  const isRangeEdge = (day) => {
    return day === selectedRange.start || day === selectedRange.end
  }

  const isRangeMiddle = (day) => {
    return isDaySelected(day) && !isRangeEdge(day)
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

      <main className="px-8 pb-8 pt-11">
        <h1 className="text-center text-4xl font-bold text-[#303244]">Elige la fecha</h1>

        <div className="mt-12 flex items-center justify-between">
          <p className="text-2xl text-[#303244]">
            {monthNames[month]} <span className="ml-3">{year}</span>
          </p>
          <div className="flex items-center gap-5 text-rojo-principal">
            <button
              className="grid h-9 w-9 place-items-center rounded-full hover:bg-red-50"
              aria-label="Mes anterior"
              onClick={() => changeMonth(-1)}
            >
              <ChevronLeftIcon className="h-6 w-6" />
            </button>
            <button
              className="grid h-9 w-9 place-items-center rounded-full hover:bg-red-50"
              aria-label="Mes siguiente"
              onClick={() => changeMonth(1)}
            >
              <ChevronRightIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        <div className="mt-10 grid grid-cols-7 gap-y-8 text-center">
          {weekDays.map((day) => (
            <div key={day} className="text-2xl font-medium text-[#303244]">
              {day}
            </div>
          ))}

          {calendarCells.map((day, index) => (
            <div key={`${day || 'empty'}-${index}`} className="grid h-11 place-items-center">
              {day && (
                <button
                  className={`grid h-11 w-11 place-items-center rounded-full text-2xl transition-colors ${
                    isRangeEdge(day)
                      ? 'bg-rojo-principal text-white'
                      : isRangeMiddle(day)
                        ? 'text-rojo-principal hover:bg-red-50'
                        : 'text-gray-500 hover:bg-gray-100'
                  }`}
                  onClick={() => selectRangeDay(day)}
                >
                  {day}
                </button>
              )}
            </div>
          ))}
        </div>

        <button
          className="mt-40 w-full rounded-3xl bg-rojo-principal px-6 py-6 text-xl font-bold text-white shadow-lg hover-rojo"
          onClick={onNext}
        >
          Siguiente
        </button>
      </main>
    </div>
  )
}

function TripPreferences({ preferences, setPreferences, onBack, onNext }) {
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

function JamGroup({ destination, selectedRange, travelers, onBack, onOpenExpenses, onNext }) {
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

function GroupExpenses({ destination, selectedRange, travelers, onBack }) {
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

function TripItinerary({ destination, selectedRange, travelers, onBack }) {
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

function formatSelectedRange(selectedRange) {
  if (!selectedRange.start) {
    return '6 - 12 Feb 2027'
  }

  if (!selectedRange.end) {
    return `${selectedRange.start} Feb 2027`
  }

  return `${selectedRange.start} - ${selectedRange.end} Feb 2027`
}

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

function ActionTile({ label, icon: Icon }) {
  return (
    <button className="flex min-h-20 flex-col items-center justify-center gap-2 rounded-2xl border border-gray-100 bg-white text-sm shadow-sm">
      <Icon className="h-8 w-8 text-rojo-principal" />
      <span>{label}</span>
    </button>
  )
}

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

function BottomNav({ currentNavTab, setCurrentNavTab }) {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-10 mx-auto flex max-w-[1126px] items-center justify-around rounded-t-[2rem] bg-white px-4 pb-5 pt-4 shadow-[0_-14px_40px_rgba(22,30,46,0.08)]">
      {navItems.slice(0, 2).map((item) => (
        <NavButton key={item.id} item={item} active={currentNavTab === item.id} onClick={setCurrentNavTab} />
      ))}

      <button
        className="grid h-20 w-20 -translate-y-6 place-items-center rounded-full bg-rojo-principal text-white shadow-lg"
        aria-label="Buscar"
        onClick={() => setCurrentNavTab('search')}
      >
        <SearchIcon className="h-10 w-10" />
      </button>

      {navItems.slice(2).map((item) => (
        <NavButton key={item.id} item={item} active={currentNavTab === item.id} onClick={setCurrentNavTab} />
      ))}
    </nav>
  )
}

function NavButton({ item, active, onClick }) {
  const Icon = item.icon

  return (
    <button
      className={`flex min-w-16 flex-col items-center gap-1 text-sm font-medium transition-colors ${
        active ? 'text-rojo-principal' : 'text-gray-500'
      }`}
      onClick={() => onClick(item.id)}
    >
      <Icon className="h-7 w-7" />
      <span>{item.label}</span>
    </button>
  )
}

function ArrowLeftIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M19 12H5" />
      <path d="m12 19-7-7 7-7" />
    </svg>
  )
}

function ChevronLeftIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m15 18-6-6 6-6" />
    </svg>
  )
}

function ChevronRightIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m9 18 6-6-6-6" />
    </svg>
  )
}

function BellIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  )
}

function HomeIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m3 11 9-8 9 8" />
      <path d="M5 10v10h14V10" />
      <path d="M9 20v-6h6v6" />
    </svg>
  )
}

function CalendarIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M8 2v4" />
      <path d="M16 2v4" />
      <rect width="18" height="18" x="3" y="4" rx="2" />
      <path d="M3 10h18" />
      <path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01" />
    </svg>
  )
}

function ChatIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
      <path d="M8 10h.01M12 10h.01M16 10h.01" />
    </svg>
  )
}

function UserIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 21a8 8 0 0 0-16 0" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  )
}

function GroupIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M16 21v-2a4 4 0 0 0-8 0v2" />
      <circle cx="12" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      <path d="M2 21v-2a4 4 0 0 1 3-3.87" />
      <path d="M8 3.13a4 4 0 0 0 0 7.75" />
    </svg>
  )
}

function UserPlusIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M16 21v-2a4 4 0 0 0-8 0v2" />
      <circle cx="12" cy="7" r="4" />
      <path d="M19 8v6" />
      <path d="M22 11h-6" />
    </svg>
  )
}

function ChartIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M6 20V10" />
      <path d="M12 20V4" />
      <path d="M18 20v-7" />
    </svg>
  )
}

function WalletIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M19 7V5a2 2 0 0 0-2.4-2L5 5.3A2 2 0 0 0 3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z" />
      <path d="M16 12h.01" />
    </svg>
  )
}

function ForkIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 3v8" />
      <path d="M8 3v8" />
      <path d="M6 3v18" />
      <path d="M14 3v18" />
      <path d="M14 3c4 2 6 5 6 9h-6" />
    </svg>
  )
}

function UmbrellaIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 12a8 8 0 0 1 16 0Z" />
      <path d="M12 12v8" />
      <path d="M12 20a3 3 0 0 0 3-3" />
      <path d="M7 12a5 5 0 0 1 10 0" />
    </svg>
  )
}

function CheersIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M8 22h4" />
      <path d="M10 16v6" />
      <path d="M6 3h8l-1 8a3 3 0 0 1-6 0Z" />
      <path d="M17 22h3" />
      <path d="M18.5 16v6" />
      <path d="M16 6h6l-.8 6a2.7 2.7 0 0 1-5.4 0Z" />
    </svg>
  )
}

function MoneyIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v10" />
      <path d="M15 9.5A3 3 0 0 0 12 8c-1.7 0-3 .9-3 2s1.3 2 3 2 3 .9 3 2-1.3 2-3 2a3 3 0 0 1-3-1.5" />
    </svg>
  )
}

function CheckCircleIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="9" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  )
}

function AlertCircleIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v5" />
      <path d="M12 17h.01" />
    </svg>
  )
}

function BuildingIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16" />
      <path d="M16 8h2a2 2 0 0 1 2 2v11" />
      <path d="M3 21h18" />
      <path d="M8 7h2M8 11h2M8 15h2" />
    </svg>
  )
}

function BusIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M6 19v2" />
      <path d="M18 19v2" />
      <rect width="16" height="14" x="4" y="3" rx="2" />
      <path d="M4 11h16" />
      <path d="M8 16h.01M16 16h.01" />
    </svg>
  )
}

function SailboatIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3v13" />
      <path d="M12 3 5 16h7" />
      <path d="M12 6 19 16h-7" />
      <path d="M4 19h16" />
      <path d="M6 21h12" />
    </svg>
  )
}

function PercentIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m19 5-14 14" />
      <circle cx="7" cy="7" r="2" />
      <circle cx="17" cy="17" r="2" />
    </svg>
  )
}

function ClockIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  )
}

function BriefcaseIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M10 6V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v1" />
      <rect width="18" height="14" x="3" y="6" rx="2" />
      <path d="M3 12h18" />
    </svg>
  )
}

function CalendarCheckIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M8 2v4M16 2v4" />
      <rect width="18" height="18" x="3" y="4" rx="2" />
      <path d="M3 10h18" />
      <path d="m9 16 2 2 4-4" />
    </svg>
  )
}

function SunIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  )
}

function SparklesIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M11 2 8.7 8.7 2 11l6.7 2.3L11 20l2.3-6.7L20 11l-6.7-2.3Z" />
      <path d="m19 3-1 3-3 1 3 1 1 3 1-3 3-1-3-1Z" />
    </svg>
  )
}

function PlusCircleIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v8M8 12h8" />
    </svg>
  )
}

function MapPinIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}

function ShareIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3v12" />
      <path d="m7 8 5-5 5 5" />
      <path d="M5 12v7h14v-7" />
    </svg>
  )
}

function SearchIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>
  )
}

function BookmarkIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M19 21 12 17 5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
    </svg>
  )
}

function PinIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}

function StarIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="m12 2 2.84 6.1 6.66.8-4.92 4.57 1.3 6.53L12 16.74 6.12 20l1.3-6.53L2.5 8.9l6.66-.8z" />
    </svg>
  )
}

function EyeIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EyeOffIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m3 3 18 18" />
      <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
      <path d="M9.9 4.2A10.3 10.3 0 0 1 12 4c6.5 0 10 8 10 8a17.8 17.8 0 0 1-3 4.3" />
      <path d="M6.2 6.2C3.5 8 2 12 2 12s3.5 8 10 8a10.9 10.9 0 0 0 5.1-1.3" />
    </svg>
  )
}

export default App
