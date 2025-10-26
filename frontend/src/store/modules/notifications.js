import api from '@/services/api'

const state = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null
}

const mutations = {
  SET_NOTIFICATIONS(state, notifications) {
    state.notifications = notifications
  },
  ADD_NOTIFICATION(state, notification) {
    state.notifications.unshift(notification)
    if (!notification.read) {
      state.unreadCount++
    }
  },
  MARK_AS_READ(state, id) {
    const notification = state.notifications.find(n => n.id === id)
    if (notification && !notification.read) {
      notification.read = true
      state.unreadCount--
    }
  },
  MARK_ALL_AS_READ(state) {
    state.notifications.forEach(n => {
      n.read = true
    })
    state.unreadCount = 0
  },
  SET_UNREAD_COUNT(state, count) {
    state.unreadCount = count
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  }
}

const actions = {
  async loadNotifications({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await api.get('/notifications/notifications/')
      commit('SET_NOTIFICATIONS', response.data.results || response.data)
      
      // Count unread notifications
      const unreadCount = (response.data.results || response.data).filter(n => !n.read).length
      commit('SET_UNREAD_COUNT', unreadCount)
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Error loading notifications'
      commit('SET_ERROR', message)
      return { success: false, error: message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async markAsRead({ commit }, id) {
    try {
      await api.patch(`/notifications/notifications/${id}/`, { read: true })
      commit('MARK_AS_READ', id)
      return { success: true }
    } catch (error) {
      console.error('Error marking notification as read:', error)
      return { success: false }
    }
  },

  async markAllAsRead({ commit }) {
    try {
      await api.post('/notifications/notifications/mark_all_read/')
      commit('MARK_ALL_AS_READ')
      return { success: true }
    } catch (error) {
      console.error('Error marking all notifications as read:', error)
      return { success: false }
    }
  },

  addNotification({ commit }, notification) {
    commit('ADD_NOTIFICATION', notification)
  }
}

const getters = {
  notifications: state => state.notifications,
  unreadCount: state => state.unreadCount,
  loading: state => state.loading,
  error: state => state.error,
  
  unreadNotifications: state => {
    return state.notifications.filter(n => !n.read)
  },
  
  notificationsByType: state => type => {
    return state.notifications.filter(n => n.type === type)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}

