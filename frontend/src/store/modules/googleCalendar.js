import googleCalendarService from '@/services/googleCalendar'

const state = {
  integrations: [],
  currentIntegration: null,
  events: [],
  syncLogs: [],
  syncStats: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    sync_status: '',
    sync_direction: '',
    search: ''
  }
}

const mutations = {
  SET_INTEGRATIONS(state, integrations) {
    state.integrations = integrations
  },
  SET_CURRENT_INTEGRATION(state, integration) {
    state.currentIntegration = integration
  },
  ADD_INTEGRATION(state, integration) {
    state.integrations.unshift(integration)
  },
  UPDATE_INTEGRATION(state, integration) {
    const index = state.integrations.findIndex(i => i.id === integration.id)
    if (index !== -1) {
      state.integrations.splice(index, 1, integration)
    }
  },
  REMOVE_INTEGRATION(state, id) {
    state.integrations = state.integrations.filter(i => i.id !== id)
  },
  SET_EVENTS(state, events) {
    state.events = events
  },
  ADD_EVENT(state, event) {
    state.events.unshift(event)
  },
  UPDATE_EVENT(state, event) {
    const index = state.events.findIndex(e => e.id === event.id)
    if (index !== -1) {
      state.events.splice(index, 1, event)
    }
  },
  REMOVE_EVENT(state, id) {
    state.events = state.events.filter(e => e.id !== id)
  },
  SET_SYNC_LOGS(state, logs) {
    state.syncLogs = logs
  },
  ADD_SYNC_LOG(state, log) {
    state.syncLogs.unshift(log)
  },
  SET_SYNC_STATS(state, stats) {
    state.syncStats = stats
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_PAGINATION(state, pagination) {
    state.pagination = pagination
  },
  SET_FILTERS(state, filters) {
    state.filters = { ...state.filters, ...filters }
  },
  CLEAR_FILTERS(state) {
    state.filters = {
      sync_status: '',
      sync_direction: '',
      search: ''
    }
  }
}

const actions = {
  async fetchIntegrations({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.getIntegrations()
      commit('SET_INTEGRATIONS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar integrações'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchIntegration({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.getIntegration(id)
      commit('SET_CURRENT_INTEGRATION', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar integração'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createIntegration({ commit }, data) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.createIntegration(data)
      commit('ADD_INTEGRATION', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao criar integração'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateIntegration({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.updateIntegration(id, data)
      commit('UPDATE_INTEGRATION', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao atualizar integração'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteIntegration({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await googleCalendarService.deleteIntegration(id)
      commit('REMOVE_INTEGRATION', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao excluir integração'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async authorizeIntegration({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.getAuthorizationUrl(id)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao autorizar integração'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async handleCallback({ commit }, { id, code }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.handleCallback(id, code)
      commit('UPDATE_INTEGRATION', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao processar callback'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async syncIntegration({ commit }, { id, options = {} }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.syncIntegration(id, options)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao sincronizar integração'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async testConnection({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.testConnection(id)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao testar conexão'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async refreshToken({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.refreshToken(id)
      commit('UPDATE_INTEGRATION', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao renovar token'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchEvents({ commit }, params = {}) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.getEvents(params)
      commit('SET_EVENTS', response.data.results || response.data)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar eventos'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createEvent({ commit }, agendamentoId) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.createEvent(agendamentoId)
      commit('ADD_EVENT', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao criar evento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async syncEventToGoogle({ commit }, eventId) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.syncEventToGoogle(eventId)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao sincronizar evento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async removeEventFromGoogle({ commit }, eventId) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.removeEventFromGoogle(eventId)
      commit('REMOVE_EVENT', eventId)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao remover evento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchSyncLogs({ commit }, params = {}) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.getSyncLogs(params)
      commit('SET_SYNC_LOGS', response.data.results || response.data)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar logs'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async syncAll({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.syncAll()
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao sincronizar tudo'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchSyncStats({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await googleCalendarService.getSyncStats()
      commit('SET_SYNC_STATS', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar estatísticas'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async checkIntegrationStatus({ commit }, userId) {
    try {
      const status = await googleCalendarService.checkIntegrationStatus(userId)
      return { success: true, data: status }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao verificar status'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    }
  },

  setFilters({ commit }, filters) {
    commit('SET_FILTERS', filters)
  },

  clearFilters({ commit }) {
    commit('CLEAR_FILTERS')
  }
}

const getters = {
  integrations: state => state.integrations,
  currentIntegration: state => state.currentIntegration,
  events: state => state.events,
  syncLogs: state => state.syncLogs,
  syncStats: state => state.syncStats,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  activeIntegrations: state => {
    return state.integrations.filter(integration => integration.sync_enabled)
  },
  
  connectedIntegrations: state => {
    return state.integrations.filter(integration => 
      integration.sync_enabled && !integration.is_token_expired
    )
  },
  
  eventsByStatus: state => status => {
    return state.events.filter(event => event.sync_status === status)
  },
  
  recentSyncLogs: state => {
    return state.syncLogs.slice(0, 10)
  },
  
  syncLogsByStatus: state => status => {
    return state.syncLogs.filter(log => log.status === status)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

