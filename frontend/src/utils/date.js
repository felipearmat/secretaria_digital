import { format, parseISO, isValid, addDays, subDays, startOfDay, endOfDay, isToday, isTomorrow, isYesterday, isThisWeek, isThisMonth, isThisYear } from 'date-fns'
import { ptBR } from 'date-fns/locale'

/**
 * Formats a date for display
 * @param {Date|string} date - Date to format
 * @param {string} formatString - Format string
 * @returns {string} Formatted date
 */
export function formatDate(date, formatString = 'dd/MM/yyyy') {
  if (!date) return ''
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    
    if (!isValid(dateObj)) {
      return ''
    }
    
    return format(dateObj, formatString, { locale: ptBR })
  } catch (error) {
    console.error('Error formatting date:', error)
    return ''
  }
}

/**
 * Formats a date and time for display
 * @param {Date|string} date - Date to format
 * @param {string} formatString - Format string
 * @returns {string} Formatted date and time
 */
export function formatDateTime(date, formatString = 'dd/MM/yyyy HH:mm') {
  return formatDate(date, formatString)
}

/**
 * Formats only the time
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted time
 */
export function formatTime(date) {
  return formatDate(date, 'HH:mm')
}

/**
 * Formats date for date input
 * @param {Date|string} date - Date to format
 * @returns {string} Date in YYYY-MM-DD format
 */
export function formatDateForInput(date) {
  return formatDate(date, 'yyyy-MM-dd')
}

/**
 * Formats date and time for datetime-local input
 * @param {Date|string} date - Date to format
 * @returns {string} Date and time in YYYY-MM-DDTHH:mm format
 */
export function formatDateTimeForInput(date) {
  return formatDate(date, "yyyy-MM-dd'T'HH:mm")
}

/**
 * Checks if a date is today
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if it's today
 */
export function isTodayDate(date) {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return isToday(dateObj)
  } catch (error) {
    return false
  }
}

/**
 * Checks if a date is tomorrow
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if it's tomorrow
 */
export function isTomorrowDate(date) {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return isTomorrow(dateObj)
  } catch (error) {
    return false
  }
}

/**
 * Checks if a date is yesterday
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if it's yesterday
 */
export function isYesterdayDate(date) {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return isYesterday(dateObj)
  } catch (error) {
    return false
  }
}

/**
 * Checks if a date is this week
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if it's this week
 */
export function isThisWeekDate(date) {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return isThisWeek(dateObj)
  } catch (error) {
    return false
  }
}

/**
 * Checks if a date is this month
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if it's this month
 */
export function isThisMonthDate(date) {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return isThisMonth(dateObj)
  } catch (error) {
    return false
  }
}

/**
 * Checks if a date is this year
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if it's this year
 */
export function isThisYearDate(date) {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return isThisYear(dateObj)
  } catch (error) {
    return false
  }
}

/**
 * Returns a relative description of the date
 * @param {Date|string} date - Date to describe
 * @returns {string} Relative description
 */
export function getRelativeDateDescription(date) {
  if (!date) return ''
  
  if (isTodayDate(date)) {
    return 'Today'
  }
  
  if (isTomorrowDate(date)) {
    return 'Tomorrow'
  }
  
  if (isYesterdayDate(date)) {
    return 'Yesterday'
  }
  
  if (isThisWeekDate(date)) {
    return 'This week'
  }
  
  if (isThisMonthDate(date)) {
    return 'This month'
  }
  
  if (isThisYearDate(date)) {
    return 'This year'
  }
  
  return formatDate(date)
}

/**
 * Adds days to a date
 * @param {Date|string} date - Base date
 * @param {number} days - Number of days to add
 * @returns {Date} New date
 */
export function addDaysToDate(date, days) {
  if (!date) return new Date()
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return addDays(dateObj, days)
  } catch (error) {
    return new Date()
  }
}

/**
 * Subtracts days from a date
 * @param {Date|string} date - Base date
 * @param {number} days - Number of days to subtract
 * @returns {Date} New date
 */
export function subDaysFromDate(date, days) {
  if (!date) return new Date()
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return subDays(dateObj, days)
  } catch (error) {
    return new Date()
  }
}

/**
 * Returns the start of the day
 * @param {Date|string} date - Base date
 * @returns {Date} Start of day
 */
export function getStartOfDay(date) {
  if (!date) return new Date()
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return startOfDay(dateObj)
  } catch (error) {
    return new Date()
  }
}

/**
 * Returns the end of the day
 * @param {Date|string} date - Base date
 * @returns {Date} End of day
 */
export function getEndOfDay(date) {
  if (!date) return new Date()
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return endOfDay(dateObj)
  } catch (error) {
    return new Date()
  }
}

/**
 * Generates an array of dates for a period
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @returns {Date[]} Array of dates
 */
export function generateDateRange(startDate, endDate) {
  if (!startDate || !endDate) return []
  
  try {
    const start = typeof startDate === 'string' ? parseISO(startDate) : startDate
    const end = typeof endDate === 'string' ? parseISO(endDate) : endDate
    
    const dates = []
    let current = start
    
    while (current <= end) {
      dates.push(new Date(current))
      current = addDays(current, 1)
    }
    
    return dates
  } catch (error) {
    return []
  }
}

/**
 * Checks if two dates are equal (ignoring time)
 * @param {Date|string} date1 - First date
 * @param {Date|string} date2 - Second date
 * @returns {boolean} True if dates are equal
 */
export function isSameDate(date1, date2) {
  if (!date1 || !date2) return false
  
  try {
    const d1 = typeof date1 === 'string' ? parseISO(date1) : date1
    const d2 = typeof date2 === 'string' ? parseISO(date2) : date2
    
    return formatDate(d1, 'yyyy-MM-dd') === formatDate(d2, 'yyyy-MM-dd')
  } catch (error) {
    return false
  }
}

/**
 * Returns current date in YYYY-MM-DD format
 * @returns {string} Current date
 */
export function getCurrentDate() {
  return formatDateForInput(new Date())
}

/**
 * Returns current date and time in YYYY-MM-DDTHH:mm format
 * @returns {string} Current date and time
 */
export function getCurrentDateTime() {
  return formatDateTimeForInput(new Date())
}

