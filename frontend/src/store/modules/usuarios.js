import api from '@/services/api'

const state = {
  usuarios: [],
  usuario: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    role: '',
    empresa: '',
    ativo: '',
    search: ''
  }
}

const mutations = {
  SET_USUARIOS(state, usuarios) {
    state.usuarios = usuarios
  },
  SET_USUARIO(state, usuario) {
    state.usuario = usuario
  },
  ADD_USUARIO(state, usuario) {
    state.usuarios.unshift(usuario)
  },
  UPDATE_USUARIO(state, usuario) {
    const index = state.usuarios.findIndex(u => u.id === usuario.id)
    if (index !== -1) {
      state.usuarios.splice(index, 1, usuario)
    }
  },
  REMOVE_USUARIO(state, id) {
    state.usuarios = state.usuarios.filter(u => u.id !== id)
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
  async fetchUsuarios({ commit, state }, params = {}) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const queryParams = {
        page: params.page || state.pagination.page,
        ...state.filters,
        ...params
      }
      
      // Remove parâmetros vazios
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === '' || queryParams[key] === null) {
          delete queryParams[key]
        }
      })
      
      const response = await api.get('/auth/usuarios/', { params: queryParams })
      
      commit('SET_USUARIOS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar usuários'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchUsuario({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/auth/usuarios/${id}/`)
      commit('SET_USUARIO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar usuário'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createUsuario({ commit }, usuarioData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/auth/usuarios/', usuarioData)
      commit('ADD_USUARIO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao criar usuário'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateUsuario({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/auth/usuarios/${id}/`, data)
      commit('UPDATE_USUARIO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao atualizar usuário'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteUsuario({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/auth/usuarios/${id}/`)
      commit('REMOVE_USUARIO', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao excluir usuário'
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
  usuarios: state => state.usuarios,
  usuario: state => state.usuario,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  usuariosPorRole: state => role => {
    return state.usuarios.filter(u => u.role === role)
  },
  
  atores: state => {
    return state.usuarios.filter(u => u.role === 'ator')
  },
  
  admins: state => {
    return state.usuarios.filter(u => ['admin', 'gerente'].includes(u.role))
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

