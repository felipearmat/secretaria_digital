import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Views
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import Agendamentos from '@/views/Agendamentos.vue'
import AgendamentoForm from '@/views/AgendamentoForm.vue'
import AgendamentoDetail from '@/views/AgendamentoDetail.vue'
import Servicos from '@/views/Servicos.vue'
import ServicoForm from '@/views/ServicoForm.vue'
import Usuarios from '@/views/Usuarios.vue'
import UsuarioForm from '@/views/UsuarioForm.vue'
import Cupons from '@/views/Cupons.vue'
import CupomForm from '@/views/CupomForm.vue'
import Relatorios from '@/views/Relatorios.vue'
import GoogleCalendarConfig from '@/views/GoogleCalendarConfig.vue'
import Perfil from '@/views/Perfil.vue'
import Configuracoes from '@/views/Configuracoes.vue'
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
    path: '/agendamentos',
    name: 'Agendamentos',
    component: Agendamentos,
    meta: {
      requiresAuth: true,
      title: 'Agendamentos'
    }
  },
  {
    path: '/agendamentos/novo',
    name: 'AgendamentoForm',
    component: AgendamentoForm,
    meta: {
      requiresAuth: true,
      title: 'Novo Agendamento'
    }
  },
  {
    path: '/agendamentos/:id',
    name: 'AgendamentoDetail',
    component: AgendamentoDetail,
    meta: {
      requiresAuth: true,
      title: 'Detalhes do Agendamento'
    }
  },
  {
    path: '/agendamentos/:id/editar',
    name: 'AgendamentoEdit',
    component: AgendamentoForm,
    meta: {
      requiresAuth: true,
      title: 'Editar Agendamento'
    }
  },
  {
    path: '/servicos',
    name: 'Servicos',
    component: Servicos,
    meta: {
      requiresAuth: true,
      title: 'Serviços'
    }
  },
  {
    path: '/servicos/novo',
    name: 'ServicoForm',
    component: ServicoForm,
    meta: {
      requiresAuth: true,
      title: 'Novo Serviço'
    }
  },
  {
    path: '/servicos/:id/editar',
    name: 'ServicoEdit',
    component: ServicoForm,
    meta: {
      requiresAuth: true,
      title: 'Editar Serviço'
    }
  },
  {
    path: '/usuarios',
    name: 'Usuarios',
    component: Usuarios,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente'],
      title: 'Usuários'
    }
  },
  {
    path: '/usuarios/novo',
    name: 'UsuarioForm',
    component: UsuarioForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente'],
      title: 'Novo Usuário'
    }
  },
  {
    path: '/usuarios/:id/editar',
    name: 'UsuarioEdit',
    component: UsuarioForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente'],
      title: 'Editar Usuário'
    }
  },
  {
    path: '/cupons',
    name: 'Cupons',
    component: Cupons,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente'],
      title: 'Cupons'
    }
  },
  {
    path: '/cupons/novo',
    name: 'CupomForm',
    component: CupomForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente'],
      title: 'Novo Cupom'
    }
  },
  {
    path: '/cupons/:id/editar',
    name: 'CupomEdit',
    component: CupomForm,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente'],
      title: 'Editar Cupom'
    }
  },
  {
    path: '/relatorios',
    name: 'Relatorios',
    component: Relatorios,
    meta: {
      requiresAuth: true,
      requiresRole: ['admin', 'gerente', 'ator'],
      title: 'Relatórios'
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
    path: '/perfil',
    name: 'Perfil',
    component: Perfil,
    meta: {
      requiresAuth: true,
      title: 'Meu Perfil'
    }
  },
  {
    path: '/configuracoes',
    name: 'Configuracoes',
    component: Configuracoes,
    meta: {
      requiresAuth: true,
      title: 'Configurações'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Página não encontrada'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard de navegação
router.beforeEach(async (to, from, next) => {
  // Verifica se a rota requer autenticação
  if (to.meta.requiresAuth) {
    const isAuthenticated = store.getters['auth/isAuthenticated']
    
    if (!isAuthenticated) {
      next('/login')
      return
    }
    
    // Verifica se o usuário tem o role necessário
    if (to.meta.requiresRole) {
      const userRole = store.getters['auth/userRole']
      const hasRequiredRole = to.meta.requiresRole.includes(userRole)
      
      if (!hasRequiredRole) {
        next('/dashboard')
        return
      }
    }
  }
  
  // Se já está logado e tenta acessar login, redireciona para dashboard
  if (to.path === '/login' && store.getters['auth/isAuthenticated']) {
    next('/dashboard')
    return
  }
  
  next()
})

// Atualiza o título da página
router.afterEach((to) => {
  document.title = `${to.meta.title || 'Secretaria Virtual'} - Secretaria Virtual`
})

export default router
