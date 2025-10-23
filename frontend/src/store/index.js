import { createStore } from 'vuex'
import auth from './modules/auth'
import agendamentos from './modules/agendamentos'
import servicos from './modules/servicos'
import usuarios from './modules/usuarios'
import cupons from './modules/cupons'
import relatorios from './modules/relatorios'
import notifications from './modules/notifications'
import googleCalendar from './modules/googleCalendar'
import ui from './modules/ui'

export default createStore({
  modules: {
    auth,
    agendamentos,
    servicos,
    usuarios,
    cupons,
    relatorios,
    notifications,
    googleCalendar,
    ui
  },
  strict: process.env.NODE_ENV !== 'production'
})
