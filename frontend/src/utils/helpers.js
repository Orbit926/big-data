export function formatSelectedRange(selectedRange) {
  if (!selectedRange || !selectedRange.start) {
    return '6 - 12 Feb 2027'
  }

  if (!selectedRange.end) {
    return `${selectedRange.start} Feb 2027`
  }

  return `${selectedRange.start} - ${selectedRange.end} Feb 2027`
}
