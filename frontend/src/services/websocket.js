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
      console.warn('[WebSocket] Token não encontrado, não conectando')
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
      console.error('[WebSocket] Erro ao conectar:', error)
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
      console.log('[WebSocket] Conectado')
      this.connected = true
      this.reconnectAttempts = 0
      this.emit('connected')
    })

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Desconectado:', reason)
      this.connected = false
      this.emit('disconnected', reason)
      
      if (reason === 'io server disconnect') {
        // Servidor forçou desconexão, não reconectar
        return
      }
      
      this.attemptReconnect()
    })

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Erro de conexão:', error)
      this.emit('error', error)
    })

    // Eventos específicos da aplicação
    this.socket.on('agendamento_criado', (data) => {
      console.log('[WebSocket] Agendamento criado:', data)
      this.emit('agendamento_criado', data)
      toast.success('Novo agendamento criado')
    })

    this.socket.on('agendamento_atualizado', (data) => {
      console.log('[WebSocket] Agendamento atualizado:', data)
      this.emit('agendamento_atualizado', data)
      toast.info('Agendamento atualizado')
    })

    this.socket.on('agendamento_cancelado', (data) => {
      console.log('[WebSocket] Agendamento cancelado:', data)
      this.emit('agendamento_cancelado', data)
      toast.warning('Agendamento cancelado')
    })

    this.socket.on('notificacao_nova', (data) => {
      console.log('[WebSocket] Nova notificação:', data)
      this.emit('notificacao_nova', data)
      toast.info(data.title || 'Nova notificação')
    })

    this.socket.on('pagamento_confirmado', (data) => {
      console.log('[WebSocket] Pagamento confirmado:', data)
      this.emit('pagamento_confirmado', data)
      toast.success('Pagamento confirmado')
    })

    this.socket.on('cupom_criado', (data) => {
      console.log('[WebSocket] Cupom criado:', data)
      this.emit('cupom_criado', data)
      toast.success('Novo cupom disponível')
    })

    this.socket.on('usuario_online', (data) => {
      console.log('[WebSocket] Usuário online:', data)
      this.emit('usuario_online', data)
    })

    this.socket.on('usuario_offline', (data) => {
      console.log('[WebSocket] Usuário offline:', data)
      this.emit('usuario_offline', data)
    })
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Máximo de tentativas de reconexão atingido')
      this.emit('reconnect_failed')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`[WebSocket] Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts} em ${delay}ms`)
    
    setTimeout(() => {
      this.connect()
    }, delay)
  }

  // Métodos para emitir eventos
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[WebSocket] Erro ao executar callback para evento ${event}:`, error)
        }
      })
    }
  }

  // Métodos para escutar eventos
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

  // Métodos para enviar eventos para o servidor
  send(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('[WebSocket] Socket não conectado, não é possível enviar evento:', event)
    }
  }

  // Métodos específicos da aplicação
  joinRoom(room) {
    this.send('join_room', { room })
  }

  leaveRoom(room) {
    this.send('leave_room', { room })
  }

  // Status da conexão
  isConnected() {
    return this.connected && this.socket
  }

  // Reconectar manualmente
  reconnect() {
    this.disconnect()
    this.reconnectAttempts = 0
    this.connect()
  }
}

// Instância singleton
const websocketService = new WebSocketService()

export default websocketService

