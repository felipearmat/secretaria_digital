import api from '@/services/api'
import router from '@/router'

const state = {
  user: null,
  token: localStorage.getItem('token'),
  loading: false,
  error: null
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
  },
  SET_TOKEN(state, token) {
    state.token = token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_AUTH(state) {
    state.user = null
    state.token = null
    state.error = null
    localStorage.removeItem('token')
  }
}

const actions = {
  async login({ commit }, credentials) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/auth/users/login/', credentials)
      const { token, user } = response.data
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      
      // Configura o token no axios
      api.defaults.headers.common['Authorization'] = `Token ${token}`
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error logging in'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async logout({ commit }) {
    try {
      await api.post('/auth/users/logout/')
    } catch (error) {
      console.error('Error logging out:', error)
    } finally {
      commit('CLEAR_AUTH')
      delete api.defaults.headers.common['Authorization']
      router.push('/login')
    }
  },

  async getCurrentUser({ commit }) {
    if (!state.token) return

    try {
      const response = await api.get('/auth/users/me/')
      commit('SET_USER', response.data)
    } catch (error) {
      console.error('Error loading current user:', error)
      commit('CLEAR_AUTH')
      router.push('/login')
    }
  },

  async updateProfile({ commit }, userData) {
    commit('SET_LOADING', true)
    
    try {
      const response = await api.patch(`/auth/users/${state.user.id}/`, userData)
      commit('SET_USER', response.data)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error updating profile'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async changePassword({ commit }, passwordData) {
    commit('SET_LOADING', true)
    
    try {
      await api.post('/auth/users/change-password/', passwordData)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error changing password'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  initializeAuth({ commit, dispatch }) {
    const token = localStorage.getItem('token')
    if (token) {
      commit('SET_TOKEN', token)
      api.defaults.headers.common['Authorization'] = `Token ${token}`
      dispatch('getCurrentUser')
    }
  }
}

const getters = {
  isAuthenticated: state => !!state.token,
  user: state => state.user,
  loading: state => state.loading,
  error: state => state.error,
  userRole: state => state.user?.role || null,
  userPermissions: state => {
    if (!state.user) return []
    
    const role = state.user.role
    const permissions = []
    
    switch (role) {
      case 'superadmin':
        permissions.push('*')
        break
      case 'admin':
        permissions.push('manage_company', 'manage_users', 'manage_appointments', 'manage_services', 'manage_coupons', 'view_reports')
        break
      case 'manager':
        permissions.push('manage_actors', 'manage_appointments', 'manage_services', 'manage_coupons', 'view_reports')
        break
      case 'actor':
        permissions.push('manage_own_appointments', 'manage_own_services', 'view_own_reports')
        break
      case 'user':
        permissions.push('view_appointments', 'create_appointments')
        break
    }
    
    return permissions
  },
  canManage: state => (resource) => {
    if (!state.user) return false
    
    const role = state.user.role
    const permissions = {
      'superadmin': ['*'],
      'admin': ['users', 'appointments', 'services', 'coupons', 'reports'],
      'manager': ['actors', 'appointments', 'services', 'coupons', 'reports'],
      'actor': ['own_appointments', 'own_services', 'own_reports'],
      'user': ['appointments']
    }
    
    return permissions[role]?.includes('*') || permissions[role]?.includes(resource) || false
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

