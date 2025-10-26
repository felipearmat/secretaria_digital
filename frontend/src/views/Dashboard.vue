<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary mb-2">
              Dashboard
            </h1>
            <p class="text-subtitle1 text-grey-darken-1">
              Welcome back, {{ user.name }}!
            </p>
          </div>
          
          <div class="d-flex align-center gap-4">
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="$router.push('/appointments/new')"
            >
              New Appointment
            </v-btn>
            
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="refreshData"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="primary" variant="flat">
          <div class="d-flex align-center">
            <v-avatar color="white" class="mr-4">
              <v-icon color="primary">mdi-calendar</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold text-white">
                {{ stats.totalAppointments }}
              </div>
              <div class="text-subtitle2 text-white">
                Total Appointments
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="success" variant="flat">
          <div class="d-flex align-center">
            <v-avatar color="white" class="mr-4">
              <v-icon color="success">mdi-currency-usd</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold text-white">
                {{ formatCurrency(stats.totalRevenue) }}
              </div>
              <div class="text-subtitle2 text-white">
                Total Revenue
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="info" variant="flat">
          <div class="d-flex align-center">
            <v-avatar color="white" class="mr-4">
              <v-icon color="info">mdi-account-group</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold text-white">
                {{ stats.totalClients }}
              </div>
              <div class="text-subtitle2 text-white">
                Total Clients
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="warning" variant="flat">
          <div class="d-flex align-center">
            <v-avatar color="white" class="mr-4">
              <v-icon color="warning">mdi-cog</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold text-white">
                {{ stats.totalServices }}
              </div>
              <div class="text-subtitle2 text-white">
                Total Services
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts and Tables -->
    <v-row>
      <!-- Upcoming Appointments -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Upcoming Appointments</span>
            <v-btn
              variant="text"
              color="primary"
              @click="$router.push('/appointments')"
            >
              View All
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="upcomingAppointments.length > 0">
              <v-list-item
                v-for="appointment in upcomingAppointments"
                :key="appointment.id"
                class="px-0"
              >
                <template v-slot:prepend>
                  <v-avatar
                    :color="getStatusColor(appointment.status)"
                    size="40"
                  >
                    <v-icon color="white">
                      {{ getStatusIcon(appointment.status) }}
                    </v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>
                  {{ appointment.service_name }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  {{ appointment.client_name }} • {{ appointment.actor_name }}
                </v-list-item-subtitle>
                
                <template v-slot:append>
                  <div class="text-right">
                    <div class="text-body2 font-weight-medium">
                      {{ formatDateTime(appointment.start_time) }}
                    </div>
                    <v-chip
                      :color="getStatusColor(appointment.status)"
                      size="small"
                      variant="flat"
                    >
                      {{ getStatusText(appointment.status) }}
                    </v-chip>
                  </div>
                </template>
              </v-list-item>
            </v-list>
            
            <v-empty-state
              v-else
              title="No upcoming appointments"
              text="You don't have any upcoming appointments at the moment."
              icon="mdi-calendar-clock"
            />
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Recent Activity -->
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>Recent Activity</v-card-title>
          
          <v-card-text>
            <v-timeline density="compact" align="start">
              <v-timeline-item
                v-for="(item, index) in recentActivity"
                :key="index"
                :dot-color="item.color"
                size="small"
              >
                <template v-slot:icon>
                  <v-icon :color="item.color" size="16">
                    {{ item.icon }}
                  </v-icon>
                </template>
                
                <div class="text-body2">
                  {{ item.text }}
                </div>
                
                <div class="text-caption text-grey-darken-1">
                  {{ formatDateTime(item.time) }}
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts -->
    <v-row class="mt-6">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Appointments by Status</v-card-title>
          
          <v-card-text>
            <div class="d-flex justify-center">
              <div style="width: 300px; height: 300px;">
                <canvas ref="statusChart"></canvas>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Monthly Revenue</v-card-title>
          
          <v-card-text>
            <div class="d-flex justify-center">
              <div style="width: 300px; height: 300px;">
                <canvas ref="revenueChart"></canvas>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import { formatDateTime } from '@/utils/date'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'Dashboard',
  data() {
    return {
      loading: false,
      stats: {
        totalAppointments: 0,
        totalRevenue: 0,
        totalClients: 0,
        totalServices: 0
      },
      recentActivity: [
        {
          text: 'New appointment created',
          time: new Date(),
          color: 'primary',
          icon: 'mdi-calendar-plus'
        },
        {
          text: 'Payment confirmed',
          time: new Date(Date.now() - 3600000),
          color: 'success',
          icon: 'mdi-credit-card'
        },
        {
          text: 'Appointment cancelled',
          time: new Date(Date.now() - 7200000),
          color: 'error',
          icon: 'mdi-calendar-remove'
        },
        {
          text: 'New client registered',
          time: new Date(Date.now() - 10800000),
          color: 'info',
          icon: 'mdi-account-plus'
        }
      ],
      statusChart: null,
      revenueChart: null
    }
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapGetters('appointments', ['upcomingAppointments'])
  },
  async mounted() {
    await this.loadDashboardData()
    this.createCharts()
  },
  methods: {
    ...mapActions('appointments', ['fetchAppointments']),
    
    async loadDashboardData() {
      this.loading = true
      
      try {
        // Load appointments
        await this.fetchAppointments({
          page_size: 5,
          ordering: 'start_time'
        })
        
        // Simulate statistics data (in production, would come from API)
        this.stats = {
          totalAppointments: 156,
          totalRevenue: 125000,
          totalClients: 89,
          totalServices: 12
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        this.$toast.error('Error loading dashboard data')
      } finally {
        this.loading = false
      }
    },
    
    async refreshData() {
      await this.loadDashboardData()
      this.createCharts()
    },
    
    createCharts() {
      this.$nextTick(() => {
        this.createStatusChart()
        this.createRevenueChart()
      })
    },
    
    createStatusChart() {
      if (this.statusChart) {
        this.statusChart.destroy()
      }
      
      const ctx = this.$refs.statusChart?.getContext('2d')
      if (!ctx) return
      
      this.statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Confirmed', 'Pending', 'Cancelled', 'Completed'],
          datasets: [{
            data: [45, 20, 15, 20],
            backgroundColor: [
              '#4CAF50',
              '#FF9800',
              '#F44336',
              '#2196F3'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    },
    
    createRevenueChart() {
      if (this.revenueChart) {
        this.revenueChart.destroy()
      }
      
      const ctx = this.$refs.revenueChart?.getContext('2d')
      if (!ctx) return
      
      this.revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Revenue',
            data: [12000, 15000, 18000, 16000, 20000, 22000],
            borderColor: '#1976D2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)',
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return 'R$ ' + value.toLocaleString()
                }
              }
            }
          }
        }
      })
    },
    
    formatDateTime,
    
    formatCurrency(value) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value)
    },
    
    getStatusColor(status) {
      const colors = {
        'pending': 'warning',
        'confirmed': 'success',
        'cancelled': 'error',
        'completed': 'info'
      }
      return colors[status] || 'grey'
    },
    
    getStatusIcon(status) {
      const icons = {
        'pending': 'mdi-clock',
        'confirmed': 'mdi-check',
        'cancelled': 'mdi-close',
        'completed': 'mdi-check-circle'
      }
      return icons[status] || 'mdi-help'
    },
    
    getStatusText(status) {
      const texts = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'cancelled': 'Cancelled',
        'completed': 'Completed'
      }
      return texts[status] || status
    }
  },
  
  beforeUnmount() {
    if (this.statusChart) {
      this.statusChart.destroy()
    }
    if (this.revenueChart) {
      this.revenueChart.destroy()
    }
  }
}
</script>

<style scoped>
.gap-4 {
  gap: 16px;
}
</style>

