import api from '@/services/api'

const state = {
  coupons: [],
  coupon: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pages: 1,
    total: 0
  },
  filters: {
    type: '',
    actor: '',
    company: '',
    active: '',
    search: ''
  }
}

const mutations = {
  SET_COUPONS(state, coupons) {
    state.coupons = coupons
  },
  SET_COUPON(state, coupon) {
    state.coupon = coupon
  },
  ADD_COUPON(state, coupon) {
    state.coupons.unshift(coupon)
  },
  UPDATE_COUPON(state, coupon) {
    const index = state.coupons.findIndex(c => c.id === coupon.id)
    if (index !== -1) {
      state.coupons.splice(index, 1, coupon)
    }
  },
  REMOVE_COUPON(state, id) {
    state.coupons = state.coupons.filter(c => c.id !== id)
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
  async fetchCoupons({ commit, state }, params = {}) {
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
      
      const response = await api.get('/payments/coupons/', { params: queryParams })
      
      commit('SET_COUPONS', response.data.results || response.data)
      
      if (response.data.count !== undefined) {
        commit('SET_PAGINATION', {
          page: response.data.page || 1,
          pages: Math.ceil(response.data.count / (response.data.page_size || 20)),
          total: response.data.count
        })
      }
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading coupons'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCoupon({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get(`/payments/coupons/${id}/`)
      commit('SET_COUPON', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading coupon'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createCoupon({ commit }, couponData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/payments/coupons/', couponData)
      commit('ADD_COUPON', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error creating coupon'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateCoupon({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.patch(`/payments/coupons/${id}/`, data)
      commit('UPDATE_COUPON', response.data)
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Error updating coupon'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteCoupon({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await api.delete(`/payments/coupons/${id}/`)
      commit('REMOVE_COUPON', id)
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error deleting coupon'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async validateCoupon({ commit }, code) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.post('/payments/coupons/validate/', { code })
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.error || 'Invalid coupon'
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
  coupons: state => state.coupons,
  coupon: state => state.coupon,
  loading: state => state.loading,
  error: state => state.error,
  pagination: state => state.pagination,
  filters: state => state.filters,
  
  activeCoupons: state => {
    return state.coupons.filter(c => c.active)
  },
  
  couponsByType: state => type => {
    return state.coupons.filter(c => c.type === type)
  },
  
  couponsByActor: state => actorId => {
    return state.coupons.filter(c => c.actor === actorId)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

