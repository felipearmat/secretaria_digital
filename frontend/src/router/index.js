import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Views
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import Appointments from '@/views/Appointments.vue'
import AppointmentForm from '@/views/AppointmentForm.vue'
import AppointmentDetail from '@/views/AppointmentDetail.vue'
import Services from '@/views/Services.vue'
import ServiceForm from '@/views/ServiceForm.vue'
import Users from '@/views/Users.vue'
import UserForm from '@/views/UserForm.vue'
import Coupons from '@/views/Coupons.vue'
import CouponForm from '@/views/CouponForm.vue'
import Reports from '@/views/Reports.vue'
import GoogleCalendarConfig from '@/views/GoogleCalendarConfig.vue'
import Profile from '@/views/Profile.vue'
import Settings from '@/views/Settings.vue'
import NotFound from '@/views/NotFound.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: 'Login'
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/appointments',
    name: 'Appointments',
    component: Appointments,
    meta: {
      requiresAuth: true,
      title: 'Appointments'
    }
  },
  {
    path: '/appointments/new',
    name: 'AppointmentForm',
    component: AppointmentForm,
    meta: {
      requiresAuth: true,
      title: 'New Appointment'
    }
  },
  {
    path: '/appointments/:id',
    name: 'AppointmentDetail',
    component: AppointmentDetail,
    meta: {
      requiresAuth: true,
      title: 'Appointment Details'
    }
  },
  {
    path: '/appointments/:id/edit',
    name: 'AppointmentEdit',
    component: AppointmentForm,
    meta: {
      requiresAuth: true,
      title: 'Edit Appointment'
    }
  },
  {
    path: '/services',
    name: 'Services',
    component: Services,
    meta: {
      requiresAuth: true,
      title: 'Services'
    }
  },
  {
    path: '/services/new',
    name: 'ServiceForm',
    component: ServiceForm,
    meta: {
      requiresAuth: true,
      title: 'New Service'
    }
  },
  {
    path: '/services/:id/edit',
    name: 'ServiceEdit',
    component: ServiceForm,
    meta: {
      requiresAuth: true,
      title: 'Edit Service'
    }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager'],
      title: 'Users'
    }
  },
  {
    path: '/users/new',
    name: 'UserForm',
    component: UserForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager'],
      title: 'New User'
    }
  },
  {
    path: '/users/:id/edit',
    name: 'UserEdit',
    component: UserForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager'],
      title: 'Edit User'
    }
  },
  {
    path: '/coupons',
    name: 'Coupons',
    component: Coupons,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager'],
      title: 'Coupons'
    }
  },
  {
    path: '/coupons/new',
    name: 'CouponForm',
    component: CouponForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager'],
      title: 'New Coupon'
    }
  },
  {
    path: '/coupons/:id/edit',
    name: 'CouponEdit',
    component: CouponForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager'],
      title: 'Edit Coupon'
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'manager', 'actor'],
      title: 'Reports'
    }
  },
  {
    path: '/google-calendar',
    name: 'GoogleCalendarConfig',
    component: GoogleCalendarConfig,
    meta: {
      requiresAuth: true,
      title: 'Google Calendar'
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      requiresAuth: true,
      title: 'My Profile'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      requiresAuth: true,
      title: 'Settings'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Page not found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  // Checks if route requires authentication
  if (to.meta.requiresAuth) {
    const isAuthenticated = store.getters['auth/isAuthenticated']
    
    if (!isAuthenticated) {
      next('/login')
      return
    }
    
    // Checks if user has required role
    if (to.meta.requiresRole) {
      const userRole = store.getters['auth/userRole']
      const hasRequiredRole = to.meta.requiresRole.includes(userRole)
      
      if (!hasRequiredRole) {
        next('/dashboard')
        return
      }
    }
  }
  
  // If already logged in and tries to access login, redirects to dashboard
  if (to.path === '/login' && store.getters['auth/isAuthenticated']) {
    next('/dashboard')
    return
  }
  
  next()
})

// Updates page title
router.afterEach((to) => {
  document.title = `${to.meta.title || 'Digital Secretary'} - Digital Secretary`
})

export default router
