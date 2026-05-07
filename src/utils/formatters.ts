export const format_date = (input: Date | string) => {
  const date = new Date(input)
  const now = Date.now()
  const diff = (now - date.getTime()) / 1000
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`
  if (diff < 86400) return date.toLocaleTimeString()

  const nowDate = new Date()

  if (nowDate.getFullYear() === date.getFullYear()) {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric'
    }).format(date)
  }

  return date.toLocaleDateString()
}