import { ArrowLeftIcon, ChevronLeftIcon, ChevronRightIcon } from './Icons'
import { monthNames, weekDays } from '../constants/travelData'

export default function DateSelection({
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
