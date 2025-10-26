const state = {
  snackbar: {
    show: false,
    message: '',
    color: 'success',
    timeout: 3000
  },
  loading: false,
  theme: 'light',
  drawer: true,
  rail: false
}

const mutations = {
  SHOW_SNACKBAR(state, { message, color = 'success', timeout = 3000 }) {
    state.snackbar = {
      show: true,
      message,
      color,
      timeout
    }
  },
  HIDE_SNACKBAR(state) {
    state.snackbar.show = false
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_THEME(state, theme) {
    state.theme = theme
  },
  SET_DRAWER(state, drawer) {
    state.drawer = drawer
  },
  SET_RAIL(state, rail) {
    state.rail = rail
  }
}

const actions = {
  showSnackbar({ commit }, { message, color = 'success', timeout = 3000 }) {
    commit('SHOW_SNACKBAR', { message, color, timeout })
  },
  
  hideSnackbar({ commit }) {
    commit('HIDE_SNACKBAR')
  },
  
  setLoading({ commit }, loading) {
    commit('SET_LOADING', loading)
  },
  
  setTheme({ commit }, theme) {
    commit('SET_THEME', theme)
  },
  
  setDrawer({ commit }, drawer) {
    commit('SET_DRAWER', drawer)
  },
  
  setRail({ commit }, rail) {
    commit('SET_RAIL', rail)
  }
}

const getters = {
  snackbar: state => state.snackbar,
  loading: state => state.loading,
  theme: state => state.theme,
  drawer: state => state.drawer,
  rail: state => state.rail
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

