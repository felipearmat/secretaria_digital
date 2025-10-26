import api from '@/services/api'

const state = {
  appointments: [],
  appointment: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    status: '',
    actor: '',
    start_date: '',
    end_date: '',
    search: ''
  }
}

const mutations = {
  SET_APPOINTMENTS(state, appointments) {
    state.appointments = appointments
  },
  SET_APPOINTMENT(state, appointment) {
    state.appointment = appointment
  },
  ADD_APPOINTMENT(state, appointment) {
    state.appointments.unshift(appointment)
  },
  UPDATE_APPOINTMENT(state, appointment) {
    const index = state.appointments.findIndex(a => a.id === appointment.id)
    if (index !== -1) {
      state.appointments.splice(index, 1, appointment)
    }
  },
  REMOVE_APPOINTMENT(state, id) {
    state.appointments = state.appointments.filter(a => a.id !== id)
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
      status: '',
      actor: '',
      start_date: '',
      end_date: '',
      search: ''
    }
  }
}

const actions = {
  async fetchAppointments({ commit, state }, params = {}) {
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
      
      const response = await api.get('/appointments/appointments/', { params: queryParams })
      
      commit('SET_APPOINTMENTS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading appointments'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchAppointment({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/appointments/appointments/${id}/`)
      commit('SET_APPOINTMENT', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading appointment'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createAppointment({ commit }, appointmentData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/appointments/appointments/', appointmentData)
      commit('ADD_APPOINTMENT', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error creating appointment'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateAppointment({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/appointments/appointments/${id}/`, data)
      commit('UPDATE_APPOINTMENT', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error updating appointment'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteAppointment({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/appointments/appointments/${id}/`)
      commit('REMOVE_APPOINTMENT', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error deleting appointment'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async confirmAppointment({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post(`/appointments/appointments/${id}/confirm/`)
      commit('UPDATE_APPOINTMENT', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error confirming appointment'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async cancelAppointment({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post(`/appointments/appointments/${id}/cancel/`)
      commit('UPDATE_APPOINTMENT', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error canceling appointment'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async getAvailability({ commit }, { actorId, date }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/appointments/appointments/availability/', {
        params: { actor_id: actorId, date }
      })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading availability'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
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
  appointments: state => state.appointments,
  appointment: state => state.appointment,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  appointmentsByStatus: state => status => {
    return state.appointments.filter(a => a.status === status)
  },
  
  appointmentsByActor: state => actorId => {
    return state.appointments.filter(a => a.actor === actorId)
  },
  
  appointmentsByDate: state => date => {
    return state.appointments.filter(a => {
      const appointmentDate = new Date(a.start_time).toDateString()
      const filterDate = new Date(date).toDateString()
      return appointmentDate === filterDate
    })
  },
  
  todayAppointments: state => {
    const today = new Date().toDateString()
    return state.appointments.filter(a => {
      const appointmentDate = new Date(a.start_time).toDateString()
      return appointmentDate === today
    })
  },
  
  upcomingAppointments: state => {
    const now = new Date()
    return state.appointments
      .filter(a => new Date(a.start_time) > now)
      .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
      .slice(0, 5)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

