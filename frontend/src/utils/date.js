import { format, parseISO, isValid, addDays, subDays, startOfDay, endOfDay, isToday, isTomorrow, isYesterday, isThisWeek, isThisMonth, isThisYear } from 'date-fns'
import { ptBR } from 'date-fns/locale'

/**
 * Formata uma data para exibição
 * @param {Date|string} date - Data para formatar
 * @param {string} formatString - String de formatação
 * @returns {string} Data formatada
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
    console.error('Erro ao formatar data:', error)
    return ''
  }
}

/**
 * Formata uma data e hora para exibição
 * @param {Date|string} date - Data para formatar
 * @param {string} formatString - String de formatação
 * @returns {string} Data e hora formatada
 */
export function formatDateTime(date, formatString = 'dd/MM/yyyy HH:mm') {
  return formatDate(date, formatString)
}

/**
 * Formata apenas a hora
 * @param {Date|string} date - Data para formatar
 * @returns {string} Hora formatada
 */
export function formatTime(date) {
  return formatDate(date, 'HH:mm')
}

/**
 * Formata data para input de data
 * @param {Date|string} date - Data para formatar
 * @returns {string} Data no formato YYYY-MM-DD
 */
export function formatDateForInput(date) {
  return formatDate(date, 'yyyy-MM-dd')
}

/**
 * Formata data e hora para input datetime-local
 * @param {Date|string} date - Data para formatar
 * @returns {string} Data e hora no formato YYYY-MM-DDTHH:mm
 */
export function formatDateTimeForInput(date) {
  return formatDate(date, "yyyy-MM-dd'T'HH:mm")
}

/**
 * Verifica se uma data é hoje
 * @param {Date|string} date - Data para verificar
 * @returns {boolean} True se for hoje
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
 * Verifica se uma data é amanhã
 * @param {Date|string} date - Data para verificar
 * @returns {boolean} True se for amanhã
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
 * Verifica se uma data é ontem
 * @param {Date|string} date - Data para verificar
 * @returns {boolean} True se for ontem
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
 * Verifica se uma data é desta semana
 * @param {Date|string} date - Data para verificar
 * @returns {boolean} True se for desta semana
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
 * Verifica se uma data é deste mês
 * @param {Date|string} date - Data para verificar
 * @returns {boolean} True se for deste mês
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
 * Verifica se uma data é deste ano
 * @param {Date|string} date - Data para verificar
 * @returns {boolean} True se for deste ano
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
 * Retorna uma descrição relativa da data
 * @param {Date|string} date - Data para descrever
 * @returns {string} Descrição relativa
 */
export function getRelativeDateDescription(date) {
  if (!date) return ''
  
  if (isTodayDate(date)) {
    return 'Hoje'
  }
  
  if (isTomorrowDate(date)) {
    return 'Amanhã'
  }
  
  if (isYesterdayDate(date)) {
    return 'Ontem'
  }
  
  if (isThisWeekDate(date)) {
    return 'Esta semana'
  }
  
  if (isThisMonthDate(date)) {
    return 'Este mês'
  }
  
  if (isThisYearDate(date)) {
    return 'Este ano'
  }
  
  return formatDate(date)
}

/**
 * Adiciona dias a uma data
 * @param {Date|string} date - Data base
 * @param {number} days - Número de dias para adicionar
 * @returns {Date} Nova data
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
 * Subtrai dias de uma data
 * @param {Date|string} date - Data base
 * @param {number} days - Número de dias para subtrair
 * @returns {Date} Nova data
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
 * Retorna o início do dia
 * @param {Date|string} date - Data base
 * @returns {Date} Início do dia
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
 * Retorna o fim do dia
 * @param {Date|string} date - Data base
 * @returns {Date} Fim do dia
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
 * Gera um array de datas para um período
 * @param {Date|string} startDate - Data de início
 * @param {Date|string} endDate - Data de fim
 * @returns {Date[]} Array de datas
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
 * Verifica se duas datas são iguais (ignorando horário)
 * @param {Date|string} date1 - Primeira data
 * @param {Date|string} date2 - Segunda data
 * @returns {boolean} True se as datas forem iguais
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
 * Retorna a data atual no formato YYYY-MM-DD
 * @returns {string} Data atual
 */
export function getCurrentDate() {
  return formatDateForInput(new Date())
}

/**
 * Retorna a data e hora atuais no formato YYYY-MM-DDTHH:mm
 * @returns {string} Data e hora atuais
 */
export function getCurrentDateTime() {
  return formatDateTimeForInput(new Date())
}

