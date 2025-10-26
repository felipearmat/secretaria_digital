/**
 * Common form validations
 */

/**
 * Validates if an email is valid
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
export function isValidEmail(email) {
  if (!email) return false
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validates if a phone is valid (Brazilian format)
 * @param {string} phone - Phone to validate
 * @returns {boolean} True if valid
 */
export function isValidPhone(phone) {
  if (!phone) return false
  
  // Remove non-numeric characters
  const cleanPhone = phone.replace(/\D/g, '')
  
  // Check if it has 10 or 11 digits
  return cleanPhone.length === 10 || cleanPhone.length === 11
}

/**
 * Validates if a CPF is valid
 * @param {string} cpf - CPF to validate
 * @returns {boolean} True if valid
 */
export function isValidCPF(cpf) {
  if (!cpf) return false
  
  // Remove non-numeric characters
  const cleanCPF = cpf.replace(/\D/g, '')
  
  // Check if it has 11 digits
  if (cleanCPF.length !== 11) return false
  
  // Check if not all digits are the same
  if (/^(\d)\1{10}$/.test(cleanCPF)) return false
  
  // First check digit validation
  let sum = 0
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (10 - i)
  }
  let remainder = sum % 11
  let digit1 = remainder < 2 ? 0 : 11 - remainder
  
  if (parseInt(cleanCPF.charAt(9)) !== digit1) return false
  
  // Second check digit validation
  sum = 0
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (11 - i)
  }
  remainder = sum % 11
  let digit2 = remainder < 2 ? 0 : 11 - remainder
  
  return parseInt(cleanCPF.charAt(10)) === digit2
}

/**
 * Validates if a CNPJ is valid
 * @param {string} cnpj - CNPJ to validate
 * @returns {boolean} True if valid
 */
export function isValidCNPJ(cnpj) {
  if (!cnpj) return false
  
  // Remove non-numeric characters
  const cleanCNPJ = cnpj.replace(/\D/g, '')
  
  // Check if it has 14 digits
  if (cleanCNPJ.length !== 14) return false
  
  // Check if not all digits are the same
  if (/^(\d)\1{13}$/.test(cleanCNPJ)) return false
  
  // First check digit validation
  let sum = 0
  let weight = 2
  for (let i = 11; i >= 0; i--) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weight
    weight = weight === 9 ? 2 : weight + 1
  }
  let remainder = sum % 11
  let digit1 = remainder < 2 ? 0 : 11 - remainder
  
  if (parseInt(cleanCNPJ.charAt(12)) !== digit1) return false
  
  // Second check digit validation
  sum = 0
  weight = 2
  for (let i = 12; i >= 0; i--) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weight
    weight = weight === 9 ? 2 : weight + 1
  }
  remainder = sum % 11
  let digit2 = remainder < 2 ? 0 : 11 - remainder
  
  return parseInt(cleanCNPJ.charAt(13)) === digit2
}

/**
 * Validates if a password is strong
 * @param {string} password - Password to validate
 * @returns {object} Object with validation and messages
 */
export function validatePassword(password) {
  const result = {
    isValid: true,
    errors: []
  }
  
  if (!password) {
    result.isValid = false
    result.errors.push('Password is required')
    return result
  }
  
  if (password.length < 8) {
    result.isValid = false
    result.errors.push('Password must have at least 8 characters')
  }
  
  if (!/[A-Z]/.test(password)) {
    result.isValid = false
    result.errors.push('Password must contain at least one uppercase letter')
  }
  
  if (!/[a-z]/.test(password)) {
    result.isValid = false
    result.errors.push('Password must contain at least one lowercase letter')
  }
  
  if (!/\d/.test(password)) {
    result.isValid = false
    result.errors.push('Password must contain at least one number')
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    result.isValid = false
    result.errors.push('Password must contain at least one special character')
  }
  
  return result
}

/**
 * Validates if a date is valid
 * @param {string|Date} date - Date to validate
 * @returns {boolean} True if valid
 */
export function isValidDate(date) {
  if (!date) return false
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj instanceof Date && !isNaN(dateObj.getTime())
}

/**
 * Validates if a date is in the future
 * @param {string|Date} date - Date to validate
 * @returns {boolean} True if it is in the future
 */
export function isFutureDate(date) {
  if (!isValidDate(date)) return false
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj > new Date()
}

/**
 * Validates if a date is in the past
 * @param {string|Date} date - Date to validate
 * @returns {boolean} True if it is in the past
 */
export function isPastDate(date) {
  if (!isValidDate(date)) return false
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj < new Date()
}

/**
 * Validates if a value is a valid number
 * @param {any} value - Value to validate
 * @returns {boolean} True if it is a valid number
 */
export function isValidNumber(value) {
  return !isNaN(value) && isFinite(value) && value !== ''
}

/**
 * Validates if a value is a positive number
 * @param {any} value - Value to validate
 * @returns {boolean} True if it is a positive number
 */
export function isValidPositiveNumber(value) {
  return isValidNumber(value) && parseFloat(value) > 0
}

/**
 * Validates if a value is an integer
 * @param {any} value - Value to validate
 * @returns {boolean} True if it is an integer
 */
export function isValidInteger(value) {
  return isValidNumber(value) && Number.isInteger(parseFloat(value))
}

/**
 * Validates if a string is not empty
 * @param {string} value - String to validate
 * @returns {boolean} True if it is not empty
 */
export function isNotEmpty(value) {
  return value !== null && value !== undefined && value.toString().trim() !== ''
}

/**
 * Validates if a string has the minimum length
 * @param {string} value - String to validate
 * @param {number} minLength - Minimum length
 * @returns {boolean} True if it has the minimum length
 */
export function hasMinLength(value, minLength) {
  return isNotEmpty(value) && value.toString().length >= minLength
}

/**
 * Validates if a string has the maximum length
 * @param {string} value - String to validate
 * @param {number} maxLength - Maximum length
 * @returns {boolean} True if it has the maximum length
 */
export function hasMaxLength(value, maxLength) {
  return !isNotEmpty(value) || value.toString().length <= maxLength
}

/**
 * Validates if a string has the exact length
 * @param {string} value - String to validate
 * @param {number} length - Exact length
 * @returns {boolean} True if it has the exact length
 */
export function hasExactLength(value, length) {
  return isNotEmpty(value) && value.toString().length === length
}

/**
 * Validates if a URL is valid
 * @param {string} url - URL to validate
 * @returns {boolean} True if valid
 */
export function isValidURL(url) {
  if (!url) return false
  
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Validates if a CEP is valid (Brazilian format)
 * @param {string} cep - CEP to validate
 * @returns {boolean} True if valid
 */
export function isValidCEP(cep) {
  if (!cep) return false
  
  // Remove non-numeric characters
  const cleanCEP = cep.replace(/\D/g, '')
  
  // Check if it has 8 digits
  return cleanCEP.length === 8
}

/**
 * Validates if a value is within a range
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean} True if it is within the range
 */
export function isInRange(value, min, max) {
  if (!isValidNumber(value)) return false
  
  const numValue = parseFloat(value)
  return numValue >= min && numValue <= max
}

/**
 * Validates if a value is in a list of options
 * @param {any} value - Value to validate
 * @param {array} options - List of valid options
 * @returns {boolean} True if it is in the list
 */
export function isInOptions(value, options) {
  return options.includes(value)
}

/**
 * Validates if a value is a non-empty array
 * @param {any} value - Value to validate
 * @returns {boolean} True if it is a non-empty array
 */
export function isValidArray(value) {
  return Array.isArray(value) && value.length > 0
}

/**
 * Validates if an object is not empty
 * @param {any} value - Value to validate
 * @returns {boolean} True if it is a non-empty object
 */
export function isValidObject(value) {
  return value !== null && typeof value === 'object' && Object.keys(value).length > 0
}

