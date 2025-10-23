import api from '@/services/api'

const state = {
  servicos: [],
  servico: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    ator: '',
    empresa: '',
    ativo: '',
    search: ''
  }
}

const mutations = {
  SET_SERVICOS(state, servicos) {
    state.servicos = servicos
  },
  SET_SERVICO(state, servico) {
    state.servico = servico
  },
  ADD_SERVICO(state, servico) {
    state.servicos.unshift(servico)
  },
  UPDATE_SERVICO(state, servico) {
    const index = state.servicos.findIndex(s => s.id === servico.id)
    if (index !== -1) {
      state.servicos.splice(index, 1, servico)
    }
  },
  REMOVE_SERVICO(state, id) {
    state.servicos = state.servicos.filter(s => s.id !== id)
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
  async fetchServicos({ commit, state }, params = {}) {
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
      
      const response = await api.get('/agendamentos/servicos/', { params: queryParams })
      
      commit('SET_SERVICOS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar serviços'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchServico({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/agendamentos/servicos/${id}/`)
      commit('SET_SERVICO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar serviço'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createServico({ commit }, servicoData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/agendamentos/servicos/', servicoData)
      commit('ADD_SERVICO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao criar serviço'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateServico({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/agendamentos/servicos/${id}/`, data)
      commit('UPDATE_SERVICO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao atualizar serviço'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteServico({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/agendamentos/servicos/${id}/`)
      commit('REMOVE_SERVICO', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao excluir serviço'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchServicosPorAtor({ commit }, atorId) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/agendamentos/servicos/por_ator/', {
        params: { ator_id: atorId }
      })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar serviços do ator'
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
  servicos: state => state.servicos,
  servico: state => state.servico,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  servicosAtivos: state => {
    return state.servicos.filter(s => s.ativo)
  },
  
  servicosPorAtor: state => atorId => {
    return state.servicos.filter(s => s.ator === atorId)
  },
  
  servicosPorEmpresa: state => empresaId => {
    return state.servicos.filter(s => s.empresa === empresaId)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

