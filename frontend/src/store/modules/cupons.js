import api from '@/services/api'

const state = {
  cupons: [],
  cupom: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    tipo: '',
    ator: '',
    empresa: '',
    ativo: '',
    search: ''
  }
}

const mutations = {
  SET_CUPONS(state, cupons) {
    state.cupons = cupons
  },
  SET_CUPOM(state, cupom) {
    state.cupom = cupom
  },
  ADD_CUPOM(state, cupom) {
    state.cupons.unshift(cupom)
  },
  UPDATE_CUPOM(state, cupom) {
    const index = state.cupons.findIndex(c => c.id === cupom.id)
    if (index !== -1) {
      state.cupons.splice(index, 1, cupom)
    }
  },
  REMOVE_CUPOM(state, id) {
    state.cupons = state.cupons.filter(c => c.id !== id)
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
  async fetchCupons({ commit, state }, params = {}) {
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
      
      const response = await api.get('/pagamentos/cupons/', { params: queryParams })
      
      commit('SET_CUPONS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar cupons'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCupom({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/pagamentos/cupons/${id}/`)
      commit('SET_CUPOM', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar cupom'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createCupom({ commit }, cupomData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/pagamentos/cupons/', cupomData)
      commit('ADD_CUPOM', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao criar cupom'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateCupom({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/pagamentos/cupons/${id}/`, data)
      commit('UPDATE_CUPOM', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao atualizar cupom'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteCupom({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/pagamentos/cupons/${id}/`)
      commit('REMOVE_CUPOM', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao excluir cupom'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async validarCupom({ commit }, codigo) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/pagamentos/cupons/validar/', { codigo })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Cupom inválido'
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
  cupons: state => state.cupons,
  cupom: state => state.cupom,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  cuponsAtivos: state => {
    return state.cupons.filter(c => c.ativo)
  },
  
  cuponsPorTipo: state => tipo => {
    return state.cupons.filter(c => c.tipo === tipo)
  },
  
  cuponsPorAtor: state => atorId => {
    return state.cupons.filter(c => c.ator === atorId)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

