import api from './api'

class GoogleCalendarService {
  constructor() {
    this.baseURL = '/api/google-calendar'
  }

  // Integrations
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

  // Synchronization
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

  // Events
  async getEvents(params = {}) {
    const response = await api.get(`${this.baseURL}/events/`, { params })
    return response.data
  }

  async getEvent(id) {
    const response = await api.get(`${this.baseURL}/events/${id}/`)
    return response.data
  }

  async createEvent(appointmentId) {
    const response = await api.post(`${this.baseURL}/events/create_event/`, {
      appointment_id: appointmentId
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

  // Synchronization logs
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

  // Utilities
  async checkIntegrationStatus(userId) {
    try {
      const integrations = await this.getIntegrations()
      const userIntegration = integrations.find(integration => 
        integration.user === userId
      )
      
      return {
        hasIntegration: !!userIntegration,
        integration: userIntegration,
        isConnected: userIntegration && !userIntegration.is_token_expired,
        needsSetup: !userIntegration,
        needsReauth: userIntegration && userIntegration.is_token_expired
      }
    } catch (error) {
      console.error('Error checking integration status:', error)
      return {
        hasIntegration: false,
        integration: null,
        isConnected: false,
        needsSetup: true,
        needsReauth: false
      }
    }
  }

  // Default settings
  getDefaultSyncOptions() {
    return {
      sync_type: 'manual',
      days_back: 30,
      days_forward: 365
    }
  }

  // Validations
  validateSyncOptions(options) {
    const errors = []
    
    if (options.days_back < 1 || options.days_back > 365) {
      errors.push('Days back must be between 1 and 365')
    }
    
    if (options.days_forward < 1 || options.days_forward > 365) {
      errors.push('Days forward must be between 1 and 365')
    }
    
    if (options.days_back + options.days_forward > 400) {
      errors.push('Sum of days cannot be greater than 400')
    }
    
    return {
      isValid: errors.length === 0,
      errors
    }
  }

  // Data formatting
  formatEventData(appointment) {
    return {
      summary: `${appointment.service_name} - ${appointment.client_name}`,
      description: appointment.notes || appointment.service_description,
      start: appointment.start_time,
      end: appointment.end_time,
      attendees: [
        { email: appointment.client_email, displayName: appointment.client_name },
        { email: appointment.actor_email, displayName: appointment.actor_name }
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
      'synced': 'Synced',
      'pending': 'Pending',
      'error': 'Error',
      'conflict': 'Conflict'
    }
    return texts[status] || status
  }

  getSyncTypeText(type) {
    const texts = {
      'full': 'Full Sync',
      'incremental': 'Incremental Sync',
      'manual': 'Manual Sync',
      'automatic': 'Automatic Sync'
    }
    return texts[type] || type
  }

  getSyncDirectionText(direction) {
    const texts = {
      'bidirectional': 'Bidirectional',
      'to_google': 'To Google',
      'from_google': 'From Google'
    }
    return texts[direction] || direction
  }
}

// Singleton instance
const googleCalendarService = new GoogleCalendarService()

export default googleCalendarService

