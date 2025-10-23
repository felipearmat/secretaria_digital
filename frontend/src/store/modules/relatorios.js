import api from '@/services/api'

const state = {
  relatorios: {
    agendamentos: [],
    financeiro: [],
    atores: [],
    servicos: []
  },
  loading: false,
  error: null,
  filtros: {
    data_inicio: '',
    data_fim: '',
    ator: '',
    empresa: '',
    servico: ''
  }
}

const mutations = {
  SET_RELATORIO_AGENDAMENTOS(state, data) {
    state.relatorios.agendamentos = data
  },
  SET_RELATORIO_FINANCEIRO(state, data) {
    state.relatorios.financeiro = data
  },
  SET_RELATORIO_ATORES(state, data) {
    state.relatorios.atores = data
  },
  SET_RELATORIO_SERVICOS(state, data) {
    state.relatorios.servicos = data
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_FILTROS(state, filtros) {
    state.filtros = { ...state.filtros, ...filtros }
  }
}

const actions = {
  async fetchRelatorioAgendamentos({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/relatorios/agendamentos/', {
        params: state.filtros
      })
      commit('SET_RELATORIO_AGENDAMENTOS', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar relatório de agendamentos'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchRelatorioFinanceiro({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/relatorios/financeiro/', {
        params: state.filtros
      })
      commit('SET_RELATORIO_FINANCEIRO', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar relatório financeiro'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchRelatorioAtores({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/relatorios/atores/', {
        params: state.filtros
      })
      commit('SET_RELATORIO_ATORES', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar relatório de atores'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchRelatorioServicos({ commit, state }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/relatorios/servicos/', {
        params: state.filtros
      })
      commit('SET_RELATORIO_SERVICOS', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Erro ao carregar relatório de serviços'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  setFiltros({ commit }, filtros) {
    commit('SET_FILTROS', filtros)
  }
}

const getters = {
  relatorios: state => state.relatorios,
  loading: state => state.loading,
  error: state => state.error,
  filtros: state => state.filtros,
  
  totalAgendamentos: state => {
    return state.relatorios.agendamentos.length
  },
  
  totalReceita: state => {
    return state.relatorios.financeiro.reduce((total, item) => total + (item.receita || 0), 0)
  },
  
  totalCustos: state => {
    return state.relatorios.financeiro.reduce((total, item) => total + (item.custos || 0), 0)
  },
  
  lucroLiquido: state => {
    const receita = state.relatorios.financeiro.reduce((total, item) => total + (item.receita || 0), 0)
    const custos = state.relatorios.financeiro.reduce((total, item) => total + (item.custos || 0), 0)
    return receita - custos
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

