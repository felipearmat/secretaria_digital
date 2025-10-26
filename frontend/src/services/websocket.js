import io from 'socket.io-client'
import { useToast } from 'vue-toastification'

const toast = useToast()

class WebSocketService {
  constructor() {
    this.socket = null
    this.connected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 1000
    this.listeners = new Map()
  }

  connect() {
    if (this.socket && this.connected) {
      return
    }

    const token = localStorage.getItem('token')
    if (!token) {
      console.warn('[WebSocket] Token not found, not connecting')
      return
    }

    try {
      this.socket = io(process.env.VUE_APP_WS_URL || 'ws://localhost:8000', {
        auth: {
          token: token
        },
        transports: ['websocket', 'polling']
      })

      this.setupEventListeners()
    } catch (error) {
      console.error('[WebSocket] Connection error:', error)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.connected = false
    }
  }

  setupEventListeners() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected')
      this.connected = true
      this.reconnectAttempts = 0
      this.emit('connected')
    })

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason)
      this.connected = false
      this.emit('disconnected', reason)
      
      if (reason === 'io server disconnect') {
        // Server forced disconnection, don't reconnect
        return
      }
      
      this.attemptReconnect()
    })

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error)
      this.emit('error', error)
    })

    // Application-specific events
    this.socket.on('appointment_created', (data) => {
      console.log('[WebSocket] Appointment created:', data)
      this.emit('appointment_created', data)
      toast.success('New appointment created')
    })

    this.socket.on('appointment_updated', (data) => {
      console.log('[WebSocket] Appointment updated:', data)
      this.emit('appointment_updated', data)
      toast.info('Appointment updated')
    })

    this.socket.on('appointment_cancelled', (data) => {
      console.log('[WebSocket] Appointment cancelled:', data)
      this.emit('appointment_cancelled', data)
      toast.warning('Appointment cancelled')
    })

    this.socket.on('notification_new', (data) => {
      console.log('[WebSocket] New notification:', data)
      this.emit('notification_new', data)
      toast.info(data.title || 'New notification')
    })

    this.socket.on('payment_confirmed', (data) => {
      console.log('[WebSocket] Payment confirmed:', data)
      this.emit('payment_confirmed', data)
      toast.success('Payment confirmed')
    })

    this.socket.on('coupon_created', (data) => {
      console.log('[WebSocket] Coupon created:', data)
      this.emit('coupon_created', data)
      toast.success('New coupon available')
    })

    this.socket.on('user_online', (data) => {
      console.log('[WebSocket] User online:', data)
      this.emit('user_online', data)
    })

    this.socket.on('user_offline', (data) => {
      console.log('[WebSocket] User offline:', data)
      this.emit('user_offline', data)
    })
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Maximum reconnection attempts reached')
      this.emit('reconnect_failed')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`[WebSocket] Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`)
    
    setTimeout(() => {
      this.connect()
    }, delay)
  }

  // Methods to emit events
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[WebSocket] Error executing callback for event ${event}:`, error)
        }
      })
    }
  }

  // Methods to listen to events
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  // Methods to send events to server
  send(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('[WebSocket] Socket not connected, cannot send event:', event)
    }
  }

  // Application-specific methods
  joinRoom(room) {
    this.send('join_room', { room })
  }

  leaveRoom(room) {
    this.send('leave_room', { room })
  }

  // Connection status
  isConnected() {
    return this.connected && this.socket
  }

  // Manually reconnect
  reconnect() {
    this.disconnect()
    this.reconnectAttempts = 0
    this.connect()
  }
}

// Singleton instance
const websocketService = new WebSocketService()

export default websocketService

