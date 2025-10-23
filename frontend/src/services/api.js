import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

// Configuração base do axios
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para requisições
api.interceptors.request.use(
  (config) => {
    // Adiciona token de autenticação se disponível
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    // Log da requisição em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }
    
    return config
  },
  (error) => {
    console.error('[API] Erro na requisição:', error)
    return Promise.reject(error)
  }
)

// Interceptor para respostas
api.interceptors.response.use(
  (response) => {
    // Log da resposta em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`)
    }
    
    return response
  },
  (error) => {
    console.error('[API] Erro na resposta:', error)
    
    // Tratamento de erros específicos
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token expirado ou inválido
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
          
        case 403:
          toast.error('Acesso negado. Você não tem permissão para esta ação.')
          break
          
        case 404:
          toast.error('Recurso não encontrado.')
          break
          
        case 422:
          // Erro de validação
          if (data.errors) {
            Object.values(data.errors).forEach(errorList => {
              if (Array.isArray(errorList)) {
                errorList.forEach(error => toast.error(error))
              } else {
                toast.error(errorList)
              }
            })
          } else if (data.error) {
            toast.error(data.error)
          }
          break
          
        case 500:
          toast.error('Erro interno do servidor. Tente novamente mais tarde.')
          break
          
        default:
          if (data.error) {
            toast.error(data.error)
          } else {
            toast.error('Ocorreu um erro inesperado.')
          }
      }
    } else if (error.request) {
      // Erro de rede
      toast.error('Erro de conexão. Verifique sua internet.')
    } else {
      // Outros erros
      toast.error('Ocorreu um erro inesperado.')
    }
    
    return Promise.reject(error)
  }
)

// Métodos auxiliares
export const apiHelpers = {
  // Upload de arquivo
  async uploadFile(file, endpoint = '/upload/') {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // Download de arquivo
  async downloadFile(url, filename) {
    const response = await api.get(url, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  },
  
  // Paginação
  buildPaginationParams(page = 1, pageSize = 20, filters = {}) {
    return {
      page,
      page_size: pageSize,
      ...filters
    }
  },
  
  // Filtros de data
  buildDateFilters(dataInicio, dataFim) {
    const filters = {}
    
    if (dataInicio) {
      filters.data_inicio = dataInicio
    }
    
    if (dataFim) {
      filters.data_fim = dataFim
    }
    
    return filters
  },
  
  // Busca
  buildSearchParams(search, fields = []) {
    const params = {}
    
    if (search) {
      params.search = search
    }
    
    fields.forEach(field => {
      if (field.value) {
        params[field.key] = field.value
      }
    })
    
    return params
  }
}

export default api

