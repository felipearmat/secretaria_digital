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
        :title="rail ? '' : 'Virtual Secretary'"
        subtitle="Appointment System"
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
          :title="rail ? '' : 'Logout'"
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
            title="Settings"
            @click="$router.push('/settings')"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
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
        <v-toolbar-title>Notifications</v-toolbar-title>
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
            No notifications
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
          Close
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
      return meta.title || 'Virtual Secretary'
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
          title: 'Appointments',
          icon: 'mdi-calendar',
          to: '/appointments',
          value: 'appointments'
        },
        {
          title: 'Services',
          icon: 'mdi-cog',
          to: '/services',
          value: 'services'
        }
      ]

      // Add items based on user role
      if (this.user.role === 'admin' || this.user.role === 'manager') {
        items.push(
          {
            title: 'Users',
            icon: 'mdi-account-group',
            to: '/users',
            value: 'users'
          },
          {
            title: 'Coupons',
            icon: 'mdi-ticket-percent',
            to: '/coupons',
            value: 'coupons'
          }
        )
      }

      if (this.user.role === 'admin' || this.user.role === 'manager' || this.user.role === 'actor') {
        items.push(
          {
            title: 'Reports',
            icon: 'mdi-chart-line',
            to: '/reports',
            value: 'reports'
          }
        )
      }

      // Add Google Calendar for all authenticated users
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
        // Load initial data
        await this.loadNotifications()
      } catch (error) {
        console.error('Error initializing app:', error)
        this.showSnackbar({
          message: 'Error loading initial data',
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
        'appointment_created': 'primary',
        'appointment_confirmed': 'success',
        'appointment_cancelled': 'error',
        'reminder': 'warning',
        'payment_confirmed': 'success',
        'coupon_available': 'info',
        'system': 'grey'
      }
      return colors[type] || 'grey'
    },
    
    getNotificationIcon(type) {
      const icons = {
        'appointment_created': 'mdi-calendar-plus',
        'appointment_confirmed': 'mdi-calendar-check',
        'appointment_cancelled': 'mdi-calendar-remove',
        'reminder': 'mdi-bell',
        'payment_confirmed': 'mdi-credit-card',
        'coupon_available': 'mdi-ticket-percent',
        'system': 'mdi-information'
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
