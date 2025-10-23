/**
 * Validações comuns para formulários
 */

/**
 * Valida se um email é válido
 * @param {string} email - Email para validar
 * @returns {boolean} True se válido
 */
export function isValidEmail(email) {
  if (!email) return false
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Valida se um telefone é válido (formato brasileiro)
 * @param {string} phone - Telefone para validar
 * @returns {boolean} True se válido
 */
export function isValidPhone(phone) {
  if (!phone) return false
  
  // Remove caracteres não numéricos
  const cleanPhone = phone.replace(/\D/g, '')
  
  // Verifica se tem 10 ou 11 dígitos
  return cleanPhone.length === 10 || cleanPhone.length === 11
}

/**
 * Valida se um CPF é válido
 * @param {string} cpf - CPF para validar
 * @returns {boolean} True se válido
 */
export function isValidCPF(cpf) {
  if (!cpf) return false
  
  // Remove caracteres não numéricos
  const cleanCPF = cpf.replace(/\D/g, '')
  
  // Verifica se tem 11 dígitos
  if (cleanCPF.length !== 11) return false
  
  // Verifica se não são todos os dígitos iguais
  if (/^(\d)\1{10}$/.test(cleanCPF)) return false
  
  // Validação do primeiro dígito verificador
  let sum = 0
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (10 - i)
  }
  let remainder = sum % 11
  let digit1 = remainder < 2 ? 0 : 11 - remainder
  
  if (parseInt(cleanCPF.charAt(9)) !== digit1) return false
  
  // Validação do segundo dígito verificador
  sum = 0
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (11 - i)
  }
  remainder = sum % 11
  let digit2 = remainder < 2 ? 0 : 11 - remainder
  
  return parseInt(cleanCPF.charAt(10)) === digit2
}

/**
 * Valida se um CNPJ é válido
 * @param {string} cnpj - CNPJ para validar
 * @returns {boolean} True se válido
 */
export function isValidCNPJ(cnpj) {
  if (!cnpj) return false
  
  // Remove caracteres não numéricos
  const cleanCNPJ = cnpj.replace(/\D/g, '')
  
  // Verifica se tem 14 dígitos
  if (cleanCNPJ.length !== 14) return false
  
  // Verifica se não são todos os dígitos iguais
  if (/^(\d)\1{13}$/.test(cleanCNPJ)) return false
  
  // Validação do primeiro dígito verificador
  let sum = 0
  let weight = 2
  for (let i = 11; i >= 0; i--) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weight
    weight = weight === 9 ? 2 : weight + 1
  }
  let remainder = sum % 11
  let digit1 = remainder < 2 ? 0 : 11 - remainder
  
  if (parseInt(cleanCNPJ.charAt(12)) !== digit1) return false
  
  // Validação do segundo dígito verificador
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
 * Valida se uma senha é forte
 * @param {string} password - Senha para validar
 * @returns {object} Objeto com validação e mensagens
 */
export function validatePassword(password) {
  const result = {
    isValid: true,
    errors: []
  }
  
  if (!password) {
    result.isValid = false
    result.errors.push('Senha é obrigatória')
    return result
  }
  
  if (password.length < 8) {
    result.isValid = false
    result.errors.push('Senha deve ter pelo menos 8 caracteres')
  }
  
  if (!/[A-Z]/.test(password)) {
    result.isValid = false
    result.errors.push('Senha deve conter pelo menos uma letra maiúscula')
  }
  
  if (!/[a-z]/.test(password)) {
    result.isValid = false
    result.errors.push('Senha deve conter pelo menos uma letra minúscula')
  }
  
  if (!/\d/.test(password)) {
    result.isValid = false
    result.errors.push('Senha deve conter pelo menos um número')
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    result.isValid = false
    result.errors.push('Senha deve conter pelo menos um caractere especial')
  }
  
  return result
}

/**
 * Valida se uma data é válida
 * @param {string|Date} date - Data para validar
 * @returns {boolean} True se válida
 */
export function isValidDate(date) {
  if (!date) return false
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj instanceof Date && !isNaN(dateObj.getTime())
}

/**
 * Valida se uma data é futura
 * @param {string|Date} date - Data para validar
 * @returns {boolean} True se for futura
 */
export function isFutureDate(date) {
  if (!isValidDate(date)) return false
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj > new Date()
}

/**
 * Valida se uma data é passada
 * @param {string|Date} date - Data para validar
 * @returns {boolean} True se for passada
 */
export function isPastDate(date) {
  if (!isValidDate(date)) return false
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj < new Date()
}

/**
 * Valida se um valor é um número válido
 * @param {any} value - Valor para validar
 * @returns {boolean} True se for um número válido
 */
export function isValidNumber(value) {
  return !isNaN(value) && isFinite(value) && value !== ''
}

/**
 * Valida se um valor é um número positivo
 * @param {any} value - Valor para validar
 * @returns {boolean} True se for um número positivo
 */
export function isValidPositiveNumber(value) {
  return isValidNumber(value) && parseFloat(value) > 0
}

/**
 * Valida se um valor é um número inteiro
 * @param {any} value - Valor para validar
 * @returns {boolean} True se for um número inteiro
 */
export function isValidInteger(value) {
  return isValidNumber(value) && Number.isInteger(parseFloat(value))
}

/**
 * Valida se uma string não está vazia
 * @param {string} value - String para validar
 * @returns {boolean} True se não estiver vazia
 */
export function isNotEmpty(value) {
  return value !== null && value !== undefined && value.toString().trim() !== ''
}

/**
 * Valida se uma string tem o tamanho mínimo
 * @param {string} value - String para validar
 * @param {number} minLength - Tamanho mínimo
 * @returns {boolean} True se tiver o tamanho mínimo
 */
export function hasMinLength(value, minLength) {
  return isNotEmpty(value) && value.toString().length >= minLength
}

/**
 * Valida se uma string tem o tamanho máximo
 * @param {string} value - String para validar
 * @param {number} maxLength - Tamanho máximo
 * @returns {boolean} True se tiver o tamanho máximo
 */
export function hasMaxLength(value, maxLength) {
  return !isNotEmpty(value) || value.toString().length <= maxLength
}

/**
 * Valida se uma string tem o tamanho exato
 * @param {string} value - String para validar
 * @param {number} length - Tamanho exato
 * @returns {boolean} True se tiver o tamanho exato
 */
export function hasExactLength(value, length) {
  return isNotEmpty(value) && value.toString().length === length
}

/**
 * Valida se uma URL é válida
 * @param {string} url - URL para validar
 * @returns {boolean} True se válida
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
 * Valida se um CEP é válido (formato brasileiro)
 * @param {string} cep - CEP para validar
 * @returns {boolean} True se válido
 */
export function isValidCEP(cep) {
  if (!cep) return false
  
  // Remove caracteres não numéricos
  const cleanCEP = cep.replace(/\D/g, '')
  
  // Verifica se tem 8 dígitos
  return cleanCEP.length === 8
}

/**
 * Valida se um valor está dentro de um range
 * @param {number} value - Valor para validar
 * @param {number} min - Valor mínimo
 * @param {number} max - Valor máximo
 * @returns {boolean} True se estiver no range
 */
export function isInRange(value, min, max) {
  if (!isValidNumber(value)) return false
  
  const numValue = parseFloat(value)
  return numValue >= min && numValue <= max
}

/**
 * Valida se um valor está em uma lista de opções
 * @param {any} value - Valor para validar
 * @param {array} options - Lista de opções válidas
 * @returns {boolean} True se estiver na lista
 */
export function isInOptions(value, options) {
  return options.includes(value)
}

/**
 * Valida se um valor é um array não vazio
 * @param {any} value - Valor para validar
 * @returns {boolean} True se for um array não vazio
 */
export function isValidArray(value) {
  return Array.isArray(value) && value.length > 0
}

/**
 * Valida se um objeto não está vazio
 * @param {any} value - Valor para validar
 * @returns {boolean} True se for um objeto não vazio
 */
export function isValidObject(value) {
  return value !== null && typeof value === 'object' && Object.keys(value).length > 0
}

