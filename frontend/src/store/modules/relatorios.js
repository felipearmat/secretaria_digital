import api from '@/services/api'

const state = {
  reports: {
    appointments: [],
    financial: [],
    actors: [],
    services: []
  },
  loading: false,
  error: null,
  filters: {
    start_date: '',
    end_date: '',
    actor: '',
    company: '',
    service: ''
  }
}

const mutations = {
  SET_REPORT_APPOINTMENTS(state, data) {
    state.reports.appointments = data
  },
  SET_REPORT_FINANCIAL(state, data) {
    state.reports.financial = data
  },
  SET_REPORT_ACTORS(state, data) {
    state.reports.actors = data
  },
  SET_REPORT_SERVICES(state, data) {
    state.reports.services = data
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_FILTERS(state, filters) {
    state.filters = { ...state.filters, ...filters }
  }
}

const actions = {
  async fetchReportAppointments({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/reports/appointments/', {
        params: state.filters
      })
      commit('SET_REPORT_APPOINTMENTS', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading appointments report'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchReportFinancial({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/reports/financial/', {
        params: state.filters
      })
      commit('SET_REPORT_FINANCIAL', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading financial report'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchReportActors({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/reports/actors/', {
        params: state.filters
      })
      commit('SET_REPORT_ACTORS', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading actors report'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchReportServices({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/reports/services/', {
        params: state.filters
      })
      commit('SET_REPORT_SERVICES', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading services report'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  setFilters({ commit }, filters) {
    commit('SET_FILTERS', filters)
  }
}

const getters = {
  reports: state => state.reports,
  loading: state => state.loading,
  error: state => state.error,
  filters: state => state.filters,
  
  totalAppointments: state => {
    return state.reports.appointments.length
  },
  
  totalRevenue: state => {
    return state.reports.financial.reduce((total, item) => total + (item.revenue || 0), 0)
  },
  
  totalCosts: state => {
    return state.reports.financial.reduce((total, item) => total + (item.costs || 0), 0)
  },
  
  netProfit: state => {
    const revenue = state.reports.financial.reduce((total, item) => total + (item.revenue || 0), 0)
    const costs = state.reports.financial.reduce((total, item) => total + (item.costs || 0), 0)
    return revenue - costs
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

