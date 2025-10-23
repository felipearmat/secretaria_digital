import api from './api'

class GoogleCalendarService {
  constructor() {
    this.baseURL = '/api/google-calendar'
  }

  // Integrações
  async getIntegrations() {
    const response = await api.get(`${this.baseURL}/integrations/`)
    return response.data
  }

  async getIntegration(id) {
    const response = await api.get(`${this.baseURL}/integrations/${id}/`)
    return response.data
  }

  async createIntegration(data) {
    const response = await api.post(`${this.baseURL}/integrations/`, data)
    return response.data
  }

  async updateIntegration(id, data) {
    const response = await api.patch(`${this.baseURL}/integrations/${id}/`, data)
    return response.data
  }

  async deleteIntegration(id) {
    const response = await api.delete(`${this.baseURL}/integrations/${id}/`)
    return response.data
  }

  // OAuth
  async getAuthorizationUrl(integrationId) {
    const response = await api.post(`${this.baseURL}/integrations/${integrationId}/authorize/`)
    return response.data
  }

  async handleCallback(integrationId, code) {
    const response = await api.post(`${this.baseURL}/integrations/${integrationId}/callback/`, {
      code
    })
    return response.data
  }

  // Sincronização
  async syncIntegration(integrationId, options = {}) {
    const response = await api.post(`${this.baseURL}/integrations/${integrationId}/sync/`, {
      sync_type: 'manual',
      days_back: 30,
      days_forward: 365,
      ...options
    })
    return response.data
  }

  async testConnection(integrationId) {
    const response = await api.post(`${this.baseURL}/integrations/${integrationId}/test_connection/`)
    return response.data
  }

  async refreshToken(integrationId) {
    const response = await api.post(`${this.baseURL}/integrations/${integrationId}/refresh_token/`)
    return response.data
  }

  // Eventos
  async getEvents(params = {}) {
    const response = await api.get(`${this.baseURL}/events/`, { params })
    return response.data
  }

  async getEvent(id) {
    const response = await api.get(`${this.baseURL}/events/${id}/`)
    return response.data
  }

  async createEvent(agendamentoId) {
    const response = await api.post(`${this.baseURL}/events/create_event/`, {
      agendamento_id: agendamentoId
    })
    return response.data
  }

  async syncEventToGoogle(eventId) {
    const response = await api.post(`${this.baseURL}/events/${eventId}/sync_to_google/`)
    return response.data
  }

  async removeEventFromGoogle(eventId) {
    const response = await api.post(`${this.baseURL}/events/${eventId}/remove_from_google/`)
    return response.data
  }

  // Logs de sincronização
  async getSyncLogs(params = {}) {
    const response = await api.get(`${this.baseURL}/sync-logs/`, { params })
    return response.data
  }

  async getSyncLog(id) {
    const response = await api.get(`${this.baseURL}/sync-logs/${id}/`)
    return response.data
  }

  async syncAll() {
    const response = await api.post(`${this.baseURL}/sync-logs/sync_all/`)
    return response.data
  }

  async getSyncStats() {
    const response = await api.get(`${this.baseURL}/sync-logs/stats/`)
    return response.data
  }

  // Utilitários
  async checkIntegrationStatus(userId) {
    try {
      const integrations = await this.getIntegrations()
      const userIntegration = integrations.find(integration => 
        integration.usuario === userId
      )
      
      return {
        hasIntegration: !!userIntegration,
        integration: userIntegration,
        isConnected: userIntegration && !userIntegration.is_token_expired,
        needsSetup: !userIntegration,
        needsReauth: userIntegration && userIntegration.is_token_expired
      }
    } catch (error) {
      console.error('Erro ao verificar status da integração:', error)
      return {
        hasIntegration: false,
        integration: null,
        isConnected: false,
        needsSetup: true,
        needsReauth: false
      }
    }
  }

  // Configurações padrão
  getDefaultSyncOptions() {
    return {
      sync_type: 'manual',
      days_back: 30,
      days_forward: 365
    }
  }

  // Validações
  validateSyncOptions(options) {
    const errors = []
    
    if (options.days_back < 1 || options.days_back > 365) {
      errors.push('Dias para trás deve estar entre 1 e 365')
    }
    
    if (options.days_forward < 1 || options.days_forward > 365) {
      errors.push('Dias para frente deve estar entre 1 e 365')
    }
    
    if (options.days_back + options.days_forward > 400) {
      errors.push('A soma dos dias não pode ser maior que 400')
    }
    
    return {
      isValid: errors.length === 0,
      errors
    }
  }

  // Formatação de dados
  formatEventData(agendamento) {
    return {
      summary: `${agendamento.servico_nome} - ${agendamento.cliente_nome}`,
      description: agendamento.observacoes || agendamento.servico_descricao,
      start: agendamento.inicio,
      end: agendamento.fim,
      attendees: [
        { email: agendamento.cliente_email, displayName: agendamento.cliente_nome },
        { email: agendamento.ator_email, displayName: agendamento.ator_nome }
      ]
    }
  }

  // Status helpers
  getSyncStatusColor(status) {
    const colors = {
      'synced': 'success',
      'pending': 'warning',
      'error': 'error',
      'conflict': 'warning'
    }
    return colors[status] || 'grey'
  }

  getSyncStatusText(status) {
    const texts = {
      'synced': 'Sincronizado',
      'pending': 'Pendente',
      'error': 'Erro',
      'conflict': 'Conflito'
    }
    return texts[status] || status
  }

  getSyncTypeText(type) {
    const texts = {
      'full': 'Sincronização Completa',
      'incremental': 'Sincronização Incremental',
      'manual': 'Sincronização Manual',
      'automatic': 'Sincronização Automática'
    }
    return texts[type] || type
  }

  getSyncDirectionText(direction) {
    const texts = {
      'bidirectional': 'Bidirecional',
      'to_google': 'Para Google',
      'from_google': 'Do Google'
    }
    return texts[direction] || direction
  }
}

// Instância singleton
const googleCalendarService = new GoogleCalendarService()

export default googleCalendarService

