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
      const response = await api.post('/auth/usuarios/login/', credentials)
      const { token, user } = response.data
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      
      // Configura o token no axios
      api.defaults.headers.common['Authorization'] = `Token ${token}`
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao fazer login'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async logout({ commit }) {
    try {
      await api.post('/auth/usuarios/logout/')
    } catch (error) {
      console.error('Erro ao fazer logout:', error)
    } finally {
      commit('CLEAR_AUTH')
      delete api.defaults.headers.common['Authorization']
      router.push('/login')
    }
  },

  async getCurrentUser({ commit }) {
    if (!state.token) return

    try {
      const response = await api.get('/auth/usuarios/me/')
      commit('SET_USER', response.data)
    } catch (error) {
      console.error('Erro ao carregar usuário atual:', error)
      commit('CLEAR_AUTH')
      router.push('/login')
    }
  },

  async updateProfile({ commit }, userData) {
    commit('SET_LOADING', true)
    
    try {
      const response = await api.patch(`/auth/usuarios/${state.user.id}/`, userData)
      commit('SET_USER', response.data)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao atualizar perfil'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async changePassword({ commit }, passwordData) {
    commit('SET_LOADING', true)
    
    try {
      await api.post('/auth/usuarios/change-password/', passwordData)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao alterar senha'
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
        permissions.push('manage_company', 'manage_users', 'manage_agendamentos', 'manage_servicos', 'manage_cupons', 'view_reports')
        break
      case 'gerente':
        permissions.push('manage_actors', 'manage_agendamentos', 'manage_servicos', 'manage_cupons', 'view_reports')
        break
      case 'ator':
        permissions.push('manage_own_agendamentos', 'manage_own_servicos', 'view_own_reports')
        break
      case 'usuario':
        permissions.push('view_agendamentos', 'create_agendamentos')
        break
    }
    
    return permissions
  },
  canManage: state => (resource) => {
    if (!state.user) return false
    
    const role = state.user.role
    const permissions = {
      'superadmin': ['*'],
      'admin': ['users', 'agendamentos', 'servicos', 'cupons', 'reports'],
      'gerente': ['actors', 'agendamentos', 'servicos', 'cupons', 'reports'],
      'ator': ['own_agendamentos', 'own_servicos', 'own_reports'],
      'usuario': ['agendamentos']
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

