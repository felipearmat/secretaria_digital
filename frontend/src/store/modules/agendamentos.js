import api from '@/services/api'

const state = {
  agendamentos: [],
  agendamento: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    status: '',
    ator: '',
    data_inicio: '',
    data_fim: '',
    search: ''
  }
}

const mutations = {
  SET_AGENDAMENTOS(state, agendamentos) {
    state.agendamentos = agendamentos
  },
  SET_AGENDAMENTO(state, agendamento) {
    state.agendamento = agendamento
  },
  ADD_AGENDAMENTO(state, agendamento) {
    state.agendamentos.unshift(agendamento)
  },
  UPDATE_AGENDAMENTO(state, agendamento) {
    const index = state.agendamentos.findIndex(a => a.id === agendamento.id)
    if (index !== -1) {
      state.agendamentos.splice(index, 1, agendamento)
    }
  },
  REMOVE_AGENDAMENTO(state, id) {
    state.agendamentos = state.agendamentos.filter(a => a.id !== id)
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
      ator: '',
      data_inicio: '',
      data_fim: '',
      search: ''
    }
  }
}

const actions = {
  async fetchAgendamentos({ commit, state }, params = {}) {
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
      
      const response = await api.get('/agendamentos/agendamentos/', { params: queryParams })
      
      commit('SET_AGENDAMENTOS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar agendamentos'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchAgendamento({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/agendamentos/agendamentos/${id}/`)
      commit('SET_AGENDAMENTO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar agendamento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createAgendamento({ commit }, agendamentoData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/agendamentos/agendamentos/', agendamentoData)
      commit('ADD_AGENDAMENTO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao criar agendamento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateAgendamento({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/agendamentos/agendamentos/${id}/`, data)
      commit('UPDATE_AGENDAMENTO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao atualizar agendamento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteAgendamento({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/agendamentos/agendamentos/${id}/`)
      commit('REMOVE_AGENDAMENTO', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao excluir agendamento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async confirmAgendamento({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post(`/agendamentos/agendamentos/${id}/confirmar/`)
      commit('UPDATE_AGENDAMENTO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao confirmar agendamento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async cancelAgendamento({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post(`/agendamentos/agendamentos/${id}/cancelar/`)
      commit('UPDATE_AGENDAMENTO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao cancelar agendamento'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async getDisponibilidade({ commit }, { atorId, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/agendamentos/agendamentos/disponibilidade/', {
        params: { ator_id: atorId, data }
      })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar disponibilidade'
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
  agendamentos: state => state.agendamentos,
  agendamento: state => state.agendamento,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  agendamentosByStatus: state => status => {
    return state.agendamentos.filter(a => a.status === status)
  },
  
  agendamentosByAtor: state => atorId => {
    return state.agendamentos.filter(a => a.ator === atorId)
  },
  
  agendamentosByDate: state => date => {
    return state.agendamentos.filter(a => {
      const agendamentoDate = new Date(a.inicio).toDateString()
      const filterDate = new Date(date).toDateString()
      return agendamentoDate === filterDate
    })
  },
  
  agendamentosHoje: state => {
    const hoje = new Date().toDateString()
    return state.agendamentos.filter(a => {
      const agendamentoDate = new Date(a.inicio).toDateString()
      return agendamentoDate === hoje
    })
  },
  
  proximosAgendamentos: state => {
    const agora = new Date()
    return state.agendamentos
      .filter(a => new Date(a.inicio) > agora)
      .sort((a, b) => new Date(a.inicio) - new Date(b.inicio))
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

