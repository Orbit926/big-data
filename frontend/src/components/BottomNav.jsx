import { HomeIcon, CalendarIcon, ChatIcon, UserIcon, SearchIcon } from './Icons'
import { navItems } from '../constants/travelData'

const iconMap = {
  HomeIcon,
  CalendarIcon,
  ChatIcon,
  UserIcon,
}

function NavButton({ item, active, onClick }) {
  const Icon = iconMap[item.iconName]

  return (
    <button
      className={`flex min-w-16 flex-col items-center gap-1 text-sm font-medium transition-colors ${
        active ? 'text-rojo-principal' : 'text-gray-500'
      }`}
      onClick={() => onClick(item.id)}
    >
      {Icon && <Icon className="h-7 w-7" />}
      <span>{item.label}</span>
    </button>
  )
}

export default function BottomNav({ currentNavTab, setCurrentNavTab }) {
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
