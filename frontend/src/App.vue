<template>
  <v-app>
    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="align-center justify-center"
      persistent
    >
      <v-progress-circular
        color="primary"
        indeterminate
        size="64"
      />
    </v-overlay>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      @click="rail = false"
    >
      <v-list-item
        prepend-avatar="/icons/logo.png"
        :title="rail ? '' : 'Secretaria Virtual'"
        subtitle="Sistema de Agendamentos"
        nav
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-chevron-left"
            @click.stop="rail = !rail"
          />
        </template>
      </v-list-item>

      <v-divider />

      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :prepend-icon="item.icon"
          :title="rail ? '' : item.title"
          :value="item.value"
          :to="item.to"
          :active="item.active"
        />
      </v-list>

      <template v-slot:append>
        <v-list-item
          prepend-icon="mdi-logout"
          :title="rail ? '' : 'Sair'"
          @click="logout"
        />
      </template>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar
      :elevation="1"
      color="white"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <v-toolbar-title>
        {{ currentPageTitle }}
      </v-toolbar-title>

      <v-spacer />

      <!-- Notifications -->
      <v-btn
        icon
        @click="toggleNotifications"
      >
        <v-badge
          :content="unreadNotifications"
          :model-value="unreadNotifications > 0"
          color="error"
        >
          <v-icon>mdi-bell</v-icon>
        </v-badge>
      </v-btn>

      <!-- User Menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-avatar size="32">
              <v-img
                v-if="user.avatar"
                :src="user.avatar"
                :alt="user.name"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-list>
          <v-list-item
            prepend-icon="mdi-account"
            :title="user.name"
            :subtitle="user.role"
          />
          <v-divider />
          <v-list-item
            prepend-icon="mdi-cog"
            title="Configurações"
            @click="$router.push('/settings')"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Sair"
            @click="logout"
          />
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <!-- Notifications Panel -->
    <v-navigation-drawer
      v-model="notificationsDrawer"
      location="right"
      temporary
      width="400"
    >
      <v-toolbar>
        <v-toolbar-title>Notificações</v-toolbar-title>
        <v-spacer />
        <v-btn
          icon
          @click="notificationsDrawer = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-list>
        <v-list-item
          v-for="notification in notifications"
          :key="notification.id"
          :class="{ 'bg-grey-lighten-4': !notification.read }"
          @click="markAsRead(notification.id)"
        >
          <template v-slot:prepend>
            <v-icon
              :color="getNotificationColor(notification.type)"
              :icon="getNotificationIcon(notification.type)"
            />
          </template>

          <v-list-item-title>{{ notification.title }}</v-list-item-title>
          <v-list-item-subtitle>{{ notification.message }}</v-list-item-subtitle>
          <v-list-item-subtitle class="text-caption">
            {{ formatDate(notification.created_at) }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="notifications.length === 0">
          <v-list-item-title class="text-center text-grey">
            Nenhuma notificação
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Global Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export default {
  name: 'App',
  data() {
    return {
      drawer: true,
      rail: false,
      notificationsDrawer: false,
      loading: false
    }
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('notifications', ['notifications', 'unreadCount']),
    ...mapState('ui', ['snackbar']),
    
    currentPageTitle() {
      const route = this.$route
      const meta = route.meta || {}
      return meta.title || 'Secretaria Virtual'
    },
    
    unreadNotifications() {
      return this.unreadCount
    },
    
    menuItems() {
      const items = [
        {
          title: 'Dashboard',
          icon: 'mdi-view-dashboard',
          to: '/dashboard',
          value: 'dashboard'
        },
        {
          title: 'Agendamentos',
          icon: 'mdi-calendar',
          to: '/agendamentos',
          value: 'agendamentos'
        },
        {
          title: 'Serviços',
          icon: 'mdi-cog',
          to: '/servicos',
          value: 'servicos'
        }
      ]

      // Adiciona itens baseados no role do usuário
      if (this.user.role === 'admin' || this.user.role === 'gerente') {
        items.push(
          {
            title: 'Usuários',
            icon: 'mdi-account-group',
            to: '/usuarios',
            value: 'usuarios'
          },
          {
            title: 'Cupons',
            icon: 'mdi-ticket-percent',
            to: '/cupons',
            value: 'cupons'
          }
        )
      }

      if (this.user.role === 'admin' || this.user.role === 'gerente' || this.user.role === 'ator') {
        items.push(
          {
            title: 'Relatórios',
            icon: 'mdi-chart-line',
            to: '/relatorios',
            value: 'relatorios'
          }
        )
      }

      // Adiciona Google Calendar para todos os usuários autenticados
      items.push(
        {
          title: 'Google Calendar',
          icon: 'mdi-calendar-google',
          to: '/google-calendar',
          value: 'google-calendar'
        }
      )

      return items.map(item => ({
        ...item,
        active: this.$route.path.startsWith(item.to)
      }))
    }
  },
  mounted() {
    this.initializeApp()
  },
  methods: {
    ...mapActions('auth', ['logout']),
    ...mapActions('notifications', ['markAsRead', 'loadNotifications']),
    ...mapActions('ui', ['showSnackbar']),
    
    async initializeApp() {
      this.loading = true
      try {
        // Carrega dados iniciais
        await this.loadNotifications()
      } catch (error) {
        console.error('Erro ao inicializar app:', error)
        this.showSnackbar({
          message: 'Erro ao carregar dados iniciais',
          color: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    toggleNotifications() {
      this.notificationsDrawer = !this.notificationsDrawer
    },
    
    getNotificationColor(type) {
      const colors = {
        'agendamento_criado': 'primary',
        'agendamento_confirmado': 'success',
        'agendamento_cancelado': 'error',
        'lembrete': 'warning',
        'pagamento_confirmado': 'success',
        'cupom_disponivel': 'info',
        'sistema': 'grey'
      }
      return colors[type] || 'grey'
    },
    
    getNotificationIcon(type) {
      const icons = {
        'agendamento_criado': 'mdi-calendar-plus',
        'agendamento_confirmado': 'mdi-calendar-check',
        'agendamento_cancelado': 'mdi-calendar-remove',
        'lembrete': 'mdi-bell',
        'pagamento_confirmado': 'mdi-credit-card',
        'cupom_disponivel': 'mdi-ticket-percent',
        'sistema': 'mdi-information'
      }
      return icons[type] || 'mdi-information'
    },
    
    formatDate(date) {
      return format(new Date(date), 'dd/MM/yyyy HH:mm', { locale: ptBR })
    }
  }
}
</script>

<style scoped>
.v-navigation-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.v-app-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.08);
}
</style>
