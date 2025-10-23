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
              Bem-vindo de volta, {{ user.name }}!
            </p>
          </div>
          
          <div class="d-flex align-center gap-4">
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="$router.push('/agendamentos/novo')"
            >
              Novo Agendamento
            </v-btn>
            
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="refreshData"
              :loading="loading"
            >
              Atualizar
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Estatísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="primary" variant="flat">
          <div class="d-flex align-center">
            <v-avatar color="white" class="mr-4">
              <v-icon color="primary">mdi-calendar</v-icon>
            </v-avatar>
            <div>
              <div class="text-h4 font-weight-bold text-white">
                {{ stats.totalAgendamentos }}
              </div>
              <div class="text-subtitle2 text-white">
                Total de Agendamentos
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
                {{ formatCurrency(stats.totalReceita) }}
              </div>
              <div class="text-subtitle2 text-white">
                Receita Total
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
                {{ stats.totalClientes }}
              </div>
              <div class="text-subtitle2 text-white">
                Total de Clientes
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
                {{ stats.totalServicos }}
              </div>
              <div class="text-subtitle2 text-white">
                Total de Serviços
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Gráficos e Tabelas -->
    <v-row>
      <!-- Próximos Agendamentos -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Próximos Agendamentos</span>
            <v-btn
              variant="text"
              color="primary"
              @click="$router.push('/agendamentos')"
            >
              Ver Todos
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="proximosAgendamentos.length > 0">
              <v-list-item
                v-for="agendamento in proximosAgendamentos"
                :key="agendamento.id"
                class="px-0"
              >
                <template v-slot:prepend>
                  <v-avatar
                    :color="getStatusColor(agendamento.status)"
                    size="40"
                  >
                    <v-icon color="white">
                      {{ getStatusIcon(agendamento.status) }}
                    </v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>
                  {{ agendamento.servico_nome }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  {{ agendamento.cliente_nome }} • {{ agendamento.ator_nome }}
                </v-list-item-subtitle>
                
                <template v-slot:append>
                  <div class="text-right">
                    <div class="text-body2 font-weight-medium">
                      {{ formatDateTime(agendamento.inicio) }}
                    </div>
                    <v-chip
                      :color="getStatusColor(agendamento.status)"
                      size="small"
                      variant="flat"
                    >
                      {{ getStatusText(agendamento.status) }}
                    </v-chip>
                  </div>
                </template>
              </v-list-item>
            </v-list>
            
            <v-empty-state
              v-else
              title="Nenhum agendamento próximo"
              text="Você não tem agendamentos próximos no momento."
              icon="mdi-calendar-clock"
            />
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Atividade Recente -->
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>Atividade Recente</v-card-title>
          
          <v-card-text>
            <v-timeline density="compact" align="start">
              <v-timeline-item
                v-for="(item, index) in atividadeRecente"
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

    <!-- Gráficos -->
    <v-row class="mt-6">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Agendamentos por Status</v-card-title>
          
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
          <v-card-title>Receita por Mês</v-card-title>
          
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
        totalAgendamentos: 0,
        totalReceita: 0,
        totalClientes: 0,
        totalServicos: 0
      },
      atividadeRecente: [
        {
          text: 'Novo agendamento criado',
          time: new Date(),
          color: 'primary',
          icon: 'mdi-calendar-plus'
        },
        {
          text: 'Pagamento confirmado',
          time: new Date(Date.now() - 3600000),
          color: 'success',
          icon: 'mdi-credit-card'
        },
        {
          text: 'Agendamento cancelado',
          time: new Date(Date.now() - 7200000),
          color: 'error',
          icon: 'mdi-calendar-remove'
        },
        {
          text: 'Novo cliente cadastrado',
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
    ...mapGetters('agendamentos', ['proximosAgendamentos'])
  },
  async mounted() {
    await this.loadDashboardData()
    this.createCharts()
  },
  methods: {
    ...mapActions('agendamentos', ['fetchAgendamentos']),
    
    async loadDashboardData() {
      this.loading = true
      
      try {
        // Carrega agendamentos
        await this.fetchAgendamentos({
          page_size: 5,
          ordering: 'inicio'
        })
        
        // Simula dados de estatísticas (em produção, viria da API)
        this.stats = {
          totalAgendamentos: 156,
          totalReceita: 125000,
          totalClientes: 89,
          totalServicos: 12
        }
      } catch (error) {
        console.error('Erro ao carregar dados do dashboard:', error)
        this.$toast.error('Erro ao carregar dados do dashboard')
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
          labels: ['Confirmados', 'Pendentes', 'Cancelados', 'Concluídos'],
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
          labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
          datasets: [{
            label: 'Receita',
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
        'pendente': 'warning',
        'confirmado': 'success',
        'cancelado': 'error',
        'concluido': 'info'
      }
      return colors[status] || 'grey'
    },
    
    getStatusIcon(status) {
      const icons = {
        'pendente': 'mdi-clock',
        'confirmado': 'mdi-check',
        'cancelado': 'mdi-close',
        'concluido': 'mdi-check-circle'
      }
      return icons[status] || 'mdi-help'
    },
    
    getStatusText(status) {
      const texts = {
        'pendente': 'Pendente',
        'confirmado': 'Confirmado',
        'cancelado': 'Cancelado',
        'concluido': 'Concluído'
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

