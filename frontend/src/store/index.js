import { createStore } from 'vuex'
import auth from './modules/auth'
import appointments from './modules/appointments'
import services from './modules/services'
import users from './modules/users'
import coupons from './modules/coupons'
import reports from './modules/reports'
import notifications from './modules/notifications'
import googleCalendar from './modules/googleCalendar'
import ui from './modules/ui'

export default createStore({
  modules: {
    auth,
    appointments,
    services,
    users,
    coupons,
    reports,
    notifications,
    googleCalendar,
    ui
  },
  strict: process.env.NODE_ENV !== 'production'
})
