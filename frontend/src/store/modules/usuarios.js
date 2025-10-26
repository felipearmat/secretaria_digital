import api from '@/services/api'

const state = {
  users: [],
  user: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    role: '',
    company: '',
    active: '',
    search: ''
  }
}

const mutations = {
  SET_USERS(state, users) {
    state.users = users
  },
  SET_USER(state, user) {
    state.user = user
  },
  ADD_USER(state, user) {
    state.users.unshift(user)
  },
  UPDATE_USER(state, user) {
    const index = state.users.findIndex(u => u.id === user.id)
    if (index !== -1) {
      state.users.splice(index, 1, user)
    }
  },
  REMOVE_USER(state, id) {
    state.users = state.users.filter(u => u.id !== id)
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
  async fetchUsers({ commit, state }, params = {}) {
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
      
      const response = await api.get('/auth/users/', { params: queryParams })
      
      commit('SET_USERS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading users'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchUser({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/auth/users/${id}/`)
      commit('SET_USER', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading user'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createUser({ commit }, userData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/auth/users/', userData)
      commit('ADD_USER', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error creating user'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateUser({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/auth/users/${id}/`, data)
      commit('UPDATE_USER', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error updating user'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteUser({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/auth/users/${id}/`)
      commit('REMOVE_USER', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error deleting user'
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
  users: state => state.users,
  user: state => state.user,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  usersByRole: state => role => {
    return state.users.filter(u => u.role === role)
  },
  
  actors: state => {
    return state.users.filter(u => u.role === 'actor')
  },
  
  admins: state => {
    return state.users.filter(u => ['admin', 'manager'].includes(u.role))
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

