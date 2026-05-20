import { useState } from 'react'
import { destinations } from './constants/travelData'
import { BellIcon } from './components/Icons'
import AuthShell from './components/AuthShell'
import PasswordField from './components/PasswordField'
import BottomNav from './components/BottomNav'
import DestinationCard from './components/DestinationCard'
import DestinationDetails from './components/DestinationDetails'
import DateSelection from './components/DateSelection'
import TripPreferences from './components/TripPreferences'
import JamGroup from './components/JamGroup'
import GroupExpenses from './components/GroupExpenses'
import TripItinerary from './components/TripItinerary'

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
  const [selectedDestination, setSelectedDestination] = useState(destinations[0])
  const [calendarDate, setCalendarDate] = useState(new Date(2027, 1, 1))
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

export default App
