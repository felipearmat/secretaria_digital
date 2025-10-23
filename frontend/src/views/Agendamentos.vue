<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary mb-2">
              Agendamentos
            </h1>
            <p class="text-subtitle1 text-grey-darken-1">
              Gerencie todos os seus agendamentos
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
              prepend-icon="mdi-filter"
              @click="showFilters = !showFilters"
            >
              Filtros
            </v-btn>
            
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="loadAgendamentos"
              :loading="loading"
            >
              Atualizar
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-expand-transition>
      <v-card v-show="showFilters" class="mb-6">
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.search"
                label="Buscar"
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                clearable
                @input="debouncedSearch"
              />
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.status"
                label="Status"
                :items="statusOptions"
                variant="outlined"
                clearable
                @update:model-value="loadAgendamentos"
              />
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.ator"
                label="Ator"
                :items="atoresOptions"
                variant="outlined"
                clearable
                @update:model-value="loadAgendamentos"
              />
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.servico"
                label="Serviço"
                :items="servicosOptions"
                variant="outlined"
                clearable
                @update:model-value="loadAgendamentos"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="filters.data_inicio"
                label="Data Início"
                type="date"
                variant="outlined"
                @update:model-value="loadAgendamentos"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="filters.data_fim"
                label="Data Fim"
                type="date"
                variant="outlined"
                @update:model-value="loadAgendamentos"
              />
            </v-col>
          </v-row>
          
          <div class="d-flex justify-end gap-2 mt-4">
            <v-btn
              variant="outlined"
              @click="clearFilters"
            >
              Limpar Filtros
            </v-btn>
            
            <v-btn
              color="primary"
              @click="loadAgendamentos"
            >
              Aplicar Filtros
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- Lista de Agendamentos -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="agendamentos"
        :loading="loading"
        :items-per-page="itemsPerPage"
        :page="currentPage"
        :server-items-length="totalItems"
        @update:page="onPageChange"
        @update:items-per-page="onItemsPerPageChange"
        class="elevation-1"
      >
        <!-- Status -->
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="flat"
          >
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>
        
        <!-- Data/Hora -->
        <template v-slot:item.inicio="{ item }">
          <div>
            <div class="text-body2 font-weight-medium">
              {{ formatDate(item.inicio) }}
            </div>
            <div class="text-caption text-grey-darken-1">
              {{ formatTime(item.inicio) }}
            </div>
          </div>
        </template>
        
        <!-- Cliente -->
        <template v-slot:item.cliente_nome="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-img
                v-if="item.cliente_avatar"
                :src="item.cliente_avatar"
                :alt="item.cliente_nome"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-body2 font-weight-medium">
                {{ item.cliente_nome }}
              </div>
              <div class="text-caption text-grey-darken-1">
                {{ item.cliente_email }}
              </div>
            </div>
          </div>
        </template>
        
        <!-- Ator -->
        <template v-slot:item.ator_nome="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-img
                v-if="item.ator_avatar"
                :src="item.ator_avatar"
                :alt="item.ator_nome"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-body2 font-weight-medium">
                {{ item.ator_nome }}
              </div>
              <div class="text-caption text-grey-darken-1">
                {{ item.servico_nome }}
              </div>
            </div>
          </div>
        </template>
        
        <!-- Preço -->
        <template v-slot:item.preco_final="{ item }">
          <div class="text-body2 font-weight-medium">
            {{ formatCurrency(item.preco_final) }}
          </div>
        </template>
        
        <!-- Ações -->
        <template v-slot:item.actions="{ item }">
          <div class="d-flex align-center gap-2">
            <v-btn
              icon
              size="small"
              variant="text"
              @click="viewAgendamento(item)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            
            <v-btn
              icon
              size="small"
              variant="text"
              @click="editAgendamento(item)"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  v-bind="props"
                >
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              
              <v-list>
                <v-list-item
                  v-if="item.status === 'pendente'"
                  @click="confirmAgendamento(item)"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-check</v-icon>
                  </template>
                  <v-list-item-title>Confirmar</v-list-item-title>
                </v-list-item>
                
                <v-list-item
                  v-if="item.status === 'pendente' || item.status === 'confirmado'"
                  @click="cancelAgendamento(item)"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-close</v-icon>
                  </template>
                  <v-list-item-title>Cancelar</v-list-item-title>
                </v-list-item>
                
                <v-list-item
                  v-if="item.status === 'pendente'"
                  @click="rejectAgendamento(item)"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-close-circle</v-icon>
                  </template>
                  <v-list-item-title>Rejeitar</v-list-item-title>
                </v-list-item>
                
                <v-divider />
                
                <v-list-item
                  @click="deleteAgendamento(item)"
                  class="text-error"
                >
                  <template v-slot:prepend>
                    <v-icon color="error">mdi-delete</v-icon>
                  </template>
                  <v-list-item-title>Excluir</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog de Confirmação -->
    <v-dialog v-model="confirmDialog.show" max-width="400">
      <v-card>
        <v-card-title>{{ confirmDialog.title }}</v-card-title>
        
        <v-card-text>
          {{ confirmDialog.message }}
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="confirmDialog.show = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            :color="confirmDialog.color"
            @click="confirmAction"
            :loading="confirmDialog.loading"
          >
            {{ confirmDialog.confirmText }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import { formatDate, formatTime } from '@/utils/date'
import { debounce } from 'lodash-es'

export default {
  name: 'Agendamentos',
  data() {
    return {
      showFilters: false,
      loading: false,
      currentPage: 1,
      itemsPerPage: 20,
      totalItems: 0,
      filters: {
        search: '',
        status: '',
        ator: '',
        servico: '',
        data_inicio: '',
        data_fim: ''
      },
      statusOptions: [
        { title: 'Pendente', value: 'pendente' },
        { title: 'Confirmado', value: 'confirmado' },
        { title: 'Cancelado', value: 'cancelado' },
        { title: 'Concluído', value: 'concluido' }
      ],
      atoresOptions: [],
      servicosOptions: [],
      headers: [
        { title: 'Status', key: 'status', sortable: false },
        { title: 'Data/Hora', key: 'inicio', sortable: true },
        { title: 'Cliente', key: 'cliente_nome', sortable: false },
        { title: 'Ator/Serviço', key: 'ator_nome', sortable: false },
        { title: 'Preço', key: 'preco_final', sortable: true },
        { title: 'Ações', key: 'actions', sortable: false }
      ],
      confirmDialog: {
        show: false,
        title: '',
        message: '',
        confirmText: '',
        color: 'primary',
        loading: false,
        action: null,
        item: null
      },
      debouncedSearch: null
    }
  },
  computed: {
    ...mapState('agendamentos', ['agendamentos', 'pagination']),
    ...mapGetters('agendamentos', ['loading'])
  },
  async mounted() {
    this.debouncedSearch = debounce(this.loadAgendamentos, 500)
    await this.loadAgendamentos()
    await this.loadOptions()
  },
  methods: {
    ...mapActions('agendamentos', [
      'fetchAgendamentos',
      'confirmAgendamento',
      'cancelAgendamento',
      'deleteAgendamento'
    ]),
    
    async loadAgendamentos() {
      this.loading = true
      
      try {
        const params = {
          page: this.currentPage,
          page_size: this.itemsPerPage,
          ...this.filters
        }
        
        // Remove parâmetros vazios
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null) {
            delete params[key]
          }
        })
        
        const result = await this.fetchAgendamentos(params)
        
        if (result.success) {
          this.totalItems = this.pagination.total
        }
      } catch (error) {
        console.error('Erro ao carregar agendamentos:', error)
        this.$toast.error('Erro ao carregar agendamentos')
      } finally {
        this.loading = false
      }
    },
    
    async loadOptions() {
      // Carrega opções para filtros
      // Em produção, viria da API
      this.atoresOptions = [
        { title: 'João Silva', value: 1 },
        { title: 'Maria Santos', value: 2 },
        { title: 'Pedro Costa', value: 3 }
      ]
      
      this.servicosOptions = [
        { title: 'Consulta Médica', value: 1 },
        { title: 'Exame de Sangue', value: 2 },
        { title: 'Ultrassom', value: 3 }
      ]
    },
    
    onPageChange(page) {
      this.currentPage = page
      this.loadAgendamentos()
    },
    
    onItemsPerPageChange(itemsPerPage) {
      this.itemsPerPage = itemsPerPage
      this.currentPage = 1
      this.loadAgendamentos()
    },
    
    clearFilters() {
      this.filters = {
        search: '',
        status: '',
        ator: '',
        servico: '',
        data_inicio: '',
        data_fim: ''
      }
      this.loadAgendamentos()
    },
    
    viewAgendamento(item) {
      this.$router.push(`/agendamentos/${item.id}`)
    },
    
    editAgendamento(item) {
      this.$router.push(`/agendamentos/${item.id}/editar`)
    },
    
    confirmAgendamento(item) {
      this.confirmDialog = {
        show: true,
        title: 'Confirmar Agendamento',
        message: `Deseja confirmar o agendamento de ${item.cliente_nome}?`,
        confirmText: 'Confirmar',
        color: 'success',
        loading: false,
        action: 'confirm',
        item
      }
    },
    
    cancelAgendamento(item) {
      this.confirmDialog = {
        show: true,
        title: 'Cancelar Agendamento',
        message: `Deseja cancelar o agendamento de ${item.cliente_nome}?`,
        confirmText: 'Cancelar',
        color: 'warning',
        loading: false,
        action: 'cancel',
        item
      }
    },
    
    rejectAgendamento(item) {
      this.confirmDialog = {
        show: true,
        title: 'Rejeitar Agendamento',
        message: `Deseja rejeitar o agendamento de ${item.cliente_nome}?`,
        confirmText: 'Rejeitar',
        color: 'error',
        loading: false,
        action: 'reject',
        item
      }
    },
    
    deleteAgendamento(item) {
      this.confirmDialog = {
        show: true,
        title: 'Excluir Agendamento',
        message: `Deseja excluir permanentemente o agendamento de ${item.cliente_nome}?`,
        confirmText: 'Excluir',
        color: 'error',
        loading: false,
        action: 'delete',
        item
      }
    },
    
    async confirmAction() {
      this.confirmDialog.loading = true
      
      try {
        const { action, item } = this.confirmDialog
        
        switch (action) {
          case 'confirm':
            await this.confirmAgendamento(item.id)
            this.$toast.success('Agendamento confirmado')
            break
            
          case 'cancel':
            await this.cancelAgendamento(item.id)
            this.$toast.success('Agendamento cancelado')
            break
            
          case 'reject':
            // Implementar rejeição
            this.$toast.success('Agendamento rejeitado')
            break
            
          case 'delete':
            await this.deleteAgendamento(item.id)
            this.$toast.success('Agendamento excluído')
            break
        }
        
        this.confirmDialog.show = false
        await this.loadAgendamentos()
      } catch (error) {
        console.error('Erro ao executar ação:', error)
        this.$toast.error('Erro ao executar ação')
      } finally {
        this.confirmDialog.loading = false
      }
    },
    
    formatDate,
    formatTime,
    
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
    
    getStatusText(status) {
      const texts = {
        'pendente': 'Pendente',
        'confirmado': 'Confirmado',
        'cancelado': 'Cancelado',
        'concluido': 'Concluído'
      }
      return texts[status] || status
    }
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

.gap-4 {
  gap: 16px;
}
</style>

