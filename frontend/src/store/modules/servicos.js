import api from '@/services/api'

const state = {
  services: [],
  service: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    actor: '',
    company: '',
    active: '',
    search: ''
  }
}

const mutations = {
  SET_SERVICES(state, services) {
    state.services = services
  },
  SET_SERVICE(state, service) {
    state.service = service
  },
  ADD_SERVICE(state, service) {
    state.services.unshift(service)
  },
  UPDATE_SERVICE(state, service) {
    const index = state.services.findIndex(s => s.id === service.id)
    if (index !== -1) {
      state.services.splice(index, 1, service)
    }
  },
  REMOVE_SERVICE(state, id) {
    state.services = state.services.filter(s => s.id !== id)
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
  }
}

const actions = {
  async fetchServices({ commit, state }, params = {}) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const queryParams = {
        page: params.page || state.pagination.page,
        ...state.filters,
        ...params
      }
      
      // Remove empty parameters
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === '' || queryParams[key] === null) {
          delete queryParams[key]
        }
      })
      
      const response = await api.get('/appointments/services/', { params: queryParams })
      
      commit('SET_SERVICES', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading services'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchService({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/appointments/services/${id}/`)
      commit('SET_SERVICE', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading service'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createService({ commit }, serviceData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/appointments/services/', serviceData)
      commit('ADD_SERVICE', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error creating service'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateService({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/appointments/services/${id}/`, data)
      commit('UPDATE_SERVICE', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error updating service'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteService({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/appointments/services/${id}/`)
      commit('REMOVE_SERVICE', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error deleting service'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchServicesByActor({ commit }, actorId) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/appointments/services/by_actor/', {
        params: { actor_id: actorId }
      })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading actor services'
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
  services: state => state.services,
  service: state => state.service,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  activeServices: state => {
    return state.services.filter(s => s.active)
  },
  
  servicesByActor: state => actorId => {
    return state.services.filter(s => s.actor === actorId)
  },
  
  servicesByCompany: state => companyId => {
    return state.services.filter(s => s.company === companyId)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

