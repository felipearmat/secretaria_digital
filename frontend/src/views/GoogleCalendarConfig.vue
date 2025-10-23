<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary mb-2">
              Google Calendar
            </h1>
            <p class="text-subtitle1 text-grey-darken-1">
              Configure a integração com Google Calendar
            </p>
          </div>
          
          <div class="d-flex align-center gap-4">
            <v-btn
              color="primary"
              prepend-icon="mdi-sync"
              @click="syncAll"
              :loading="loading"
            >
              Sincronizar Tudo
            </v-btn>
            
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="loadData"
              :loading="loading"
            >
              Atualizar
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Status da Integração -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3" :color="integrationStatus.isConnected ? 'success' : 'warning'">
              {{ integrationStatus.isConnected ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
            Status da Integração
          </v-card-title>
          
          <v-card-text>
            <v-alert
              :type="integrationStatus.isConnected ? 'success' : 'warning'"
              variant="tonal"
              class="mb-4"
            >
              <div v-if="integrationStatus.needsSetup">
                <strong>Configuração Necessária:</strong> Você precisa configurar a integração com Google Calendar.
              </div>
              <div v-else-if="integrationStatus.needsReauth">
                <strong>Reautorização Necessária:</strong> Sua sessão com Google Calendar expirou. Clique em "Reautorizar" para continuar.
              </div>
              <div v-else-if="integrationStatus.isConnected">
                <strong>Conectado:</strong> Sua integração com Google Calendar está ativa e funcionando.
              </div>
            </v-alert>
            
            <div v-if="currentIntegration" class="d-flex align-center gap-4">
              <v-chip
                :color="currentIntegration.sync_enabled ? 'success' : 'error'"
                variant="flat"
              >
                {{ currentIntegration.sync_enabled ? 'Sincronização Ativa' : 'Sincronização Desabilitada' }}
              </v-chip>
              
              <v-chip
                :color="getSyncDirectionColor(currentIntegration.sync_direction)"
                variant="flat"
              >
                {{ getSyncDirectionText(currentIntegration.sync_direction) }}
              </v-chip>
              
              <v-chip
                v-if="currentIntegration.last_sync_at"
                color="info"
                variant="flat"
              >
                Última sincronização: {{ formatDateTime(currentIntegration.last_sync_at) }}
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Configuração da Integração -->
    <v-row v-if="!integrationStatus.hasIntegration || integrationStatus.needsReauth">
      <v-col cols="12">
        <v-card>
          <v-card-title>Configurar Integração</v-card-title>
          
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.calendar_id"
                    label="ID do Calendário"
                    hint="Deixe vazio para usar o calendário principal"
                    variant="outlined"
                    :rules="calendarIdRules"
                  />
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.sync_direction"
                    label="Direção da Sincronização"
                    :items="syncDirectionOptions"
                    variant="outlined"
                    :rules="syncDirectionRules"
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-switch
                    v-model="form.sync_enabled"
                    label="Habilitar Sincronização"
                    color="primary"
                  />
                </v-col>
                
                <v-col cols="12">
                  <h3 class="text-h6 mb-4">Notificações</h3>
                  
                  <v-row>
                    <v-col cols="12" md="4">
                      <v-switch
                        v-model="form.notify_on_create"
                        label="Notificar ao Criar"
                        color="primary"
                      />
                    </v-col>
                    
                    <v-col cols="12" md="4">
                      <v-switch
                        v-model="form.notify_on_update"
                        label="Notificar ao Atualizar"
                        color="primary"
                      />
                    </v-col>
                    
                    <v-col cols="12" md="4">
                      <v-switch
                        v-model="form.notify_on_delete"
                        label="Notificar ao Excluir"
                        color="primary"
                      />
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          
          <v-card-actions>
            <v-spacer />
            <v-btn
              variant="outlined"
              @click="resetForm"
            >
              Cancelar
            </v-btn>
            <v-btn
              color="primary"
              @click="handleSubmit"
              :loading="loading"
              :disabled="!valid"
            >
              {{ integrationStatus.hasIntegration ? 'Atualizar' : 'Configurar' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Configuração Existente -->
    <v-row v-else-if="currentIntegration">
      <v-col cols="12">
        <v-card>
          <v-card-title>Configuração Atual</v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="currentIntegration.calendar_id"
                  label="ID do Calendário"
                  variant="outlined"
                  readonly
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  :value="getSyncDirectionText(currentIntegration.sync_direction)"
                  label="Direção da Sincronização"
                  variant="outlined"
                  readonly
                />
              </v-col>
              
              <v-col cols="12">
                <v-switch
                  v-model="currentIntegration.sync_enabled"
                  label="Sincronização Habilitada"
                  color="primary"
                  @change="updateSyncEnabled"
                />
              </v-col>
            </v-row>
          </v-card-text>
          
          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              @click="startAuthorization"
              :loading="loading"
            >
              Reautorizar
            </v-btn>
            <v-btn
              color="success"
              @click="testConnection"
              :loading="loading"
            >
              Testar Conexão
            </v-btn>
            <v-btn
              color="warning"
              @click="refreshToken"
              :loading="loading"
            >
              Renovar Token
            </v-btn>
            <v-btn
              color="error"
              @click="deleteIntegration"
              :loading="loading"
            >
              Remover Integração
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Estatísticas de Sincronização -->
    <v-row v-if="syncStats" class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>Estatísticas de Sincronização</v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-card color="primary" variant="flat">
                  <v-card-text class="text-center">
                    <div class="text-h4 font-weight-bold text-white">
                      {{ syncStats.total_syncs }}
                    </div>
                    <div class="text-subtitle2 text-white">
                      Total de Sincronizações
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-card color="success" variant="flat">
                  <v-card-text class="text-center">
                    <div class="text-h4 font-weight-bold text-white">
                      {{ syncStats.successful_syncs }}
                    </div>
                    <div class="text-subtitle2 text-white">
                      Sincronizações Bem-sucedidas
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-card color="error" variant="flat">
                  <v-card-text class="text-center">
                    <div class="text-h4 font-weight-bold text-white">
                      {{ syncStats.error_syncs }}
                    </div>
                    <div class="text-subtitle2 text-white">
                      Sincronizações com Erro
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-card color="info" variant="flat">
                  <v-card-text class="text-center">
                    <div class="text-h4 font-weight-bold text-white">
                      {{ syncStats.success_rate.toFixed(1) }}%
                    </div>
                    <div class="text-subtitle2 text-white">
                      Taxa de Sucesso
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Logs de Sincronização -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Logs de Sincronização</span>
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="loadSyncLogs"
              :loading="loading"
            >
              Atualizar
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="syncLogHeaders"
              :items="syncLogs"
              :loading="loading"
              class="elevation-1"
            >
              <!-- Status -->
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getSyncStatusColor(item.status)"
                  size="small"
                  variant="flat"
                >
                  {{ getSyncStatusText(item.status) }}
                </v-chip>
              </template>
              
              <!-- Tipo -->
              <template v-slot:item.sync_type="{ item }">
                {{ getSyncTypeText(item.sync_type) }}
              </template>
              
              <!-- Duração -->
              <template v-slot:item.duration_display="{ item }">
                {{ item.duration_display || '-' }}
              </template>
              
              <!-- Resumo dos Eventos -->
              <template v-slot:item.events_summary="{ item }">
                {{ item.events_summary || '-' }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog de Autorização -->
    <v-dialog v-model="authDialog.show" max-width="600">
      <v-card>
        <v-card-title>Autorizar Google Calendar</v-card-title>
        
        <v-card-text>
          <p>Para usar a integração com Google Calendar, você precisa autorizar o acesso ao seu calendário.</p>
          
          <v-alert type="info" variant="tonal" class="mb-4">
            <strong>Permissões necessárias:</strong>
            <ul class="mt-2">
              <li>Ler eventos do calendário</li>
              <li>Criar eventos no calendário</li>
              <li>Atualizar eventos no calendário</li>
              <li>Excluir eventos do calendário</li>
            </ul>
          </v-alert>
          
          <p>Clique no botão abaixo para ser redirecionado para o Google e autorizar o acesso.</p>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="outlined"
            @click="authDialog.show = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            :href="authDialog.url"
            target="_blank"
            @click="authDialog.show = false"
          >
            Autorizar no Google
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import { formatDateTime } from '@/utils/date'

export default {
  name: 'GoogleCalendarConfig',
  data() {
    return {
      valid: false,
      loading: false,
      integrationStatus: {
        hasIntegration: false,
        isConnected: false,
        needsSetup: true,
        needsReauth: false,
        integration: null
      },
      form: {
        calendar_id: 'primary',
        sync_enabled: true,
        sync_direction: 'bidirectional',
        notify_on_create: true,
        notify_on_update: true,
        notify_on_delete: true
      },
      syncDirectionOptions: [
        { title: 'Bidirecional', value: 'bidirectional' },
        { title: 'Para Google', value: 'to_google' },
        { title: 'Do Google', value: 'from_google' }
      ],
      syncLogHeaders: [
        { title: 'Tipo', key: 'sync_type' },
        { title: 'Status', key: 'status' },
        { title: 'Eventos', key: 'events_summary' },
        { title: 'Duração', key: 'duration_display' },
        { title: 'Iniciado em', key: 'started_at' },
        { title: 'Concluído em', key: 'completed_at' }
      ],
      authDialog: {
        show: false,
        url: ''
      },
      calendarIdRules: [
        v => !v || v.length <= 255 || 'ID do calendário deve ter no máximo 255 caracteres'
      ],
      syncDirectionRules: [
        v => !!v || 'Direção da sincronização é obrigatória'
      ]
    }
  },
  computed: {
    ...mapState('googleCalendar', ['integrations', 'currentIntegration', 'syncLogs', 'syncStats']),
    ...mapGetters('googleCalendar', ['loading'])
  },
  async mounted() {
    await this.loadData()
    await this.checkStatus()
  },
  methods: {
    ...mapActions('googleCalendar', [
      'fetchIntegrations', 'fetchIntegration', 'createIntegration', 'updateIntegration',
      'deleteIntegration', 'authorizeIntegration', 'handleCallback', 'syncIntegration',
      'testConnection', 'refreshToken', 'fetchSyncLogs', 'syncAll', 'fetchSyncStats'
    ]),
    
    async loadData() {
      this.loading = true
      try {
        await Promise.all([
          this.fetchIntegrations(),
          this.fetchSyncLogs(),
          this.fetchSyncStats()
        ])
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
        this.$toast.error('Erro ao carregar dados')
      } finally {
        this.loading = false
      }
    },
    
    async checkStatus() {
      try {
        const result = await this.$store.dispatch('googleCalendar/checkIntegrationStatus', this.$store.state.auth.user.id)
        if (result.success) {
          this.integrationStatus = result.data
        }
      } catch (error) {
        console.error('Erro ao verificar status:', error)
      }
    },
    
    async handleSubmit() {
      if (!this.valid) return
      
      this.loading = true
      try {
        if (this.integrationStatus.hasIntegration) {
          // Atualizar integração existente
          const result = await this.updateIntegration({
            id: this.currentIntegration.id,
            data: this.form
          })
          
          if (result.success) {
            this.$toast.success('Integração atualizada com sucesso')
            await this.loadData()
          }
        } else {
          // Criar nova integração
          const result = await this.createIntegration(this.form)
          
          if (result.success) {
            this.$toast.success('Integração criada com sucesso')
            await this.loadData()
            await this.checkStatus()
          }
        }
      } catch (error) {
        console.error('Erro ao salvar integração:', error)
        this.$toast.error('Erro ao salvar integração')
      } finally {
        this.loading = false
      }
    },
    
    async startAuthorization() {
      if (!this.currentIntegration) return
      
      this.loading = true
      try {
        const result = await this.authorizeIntegration(this.currentIntegration.id)
        
        if (result.success) {
          this.authDialog.url = result.data.authorization_url
          this.authDialog.show = true
        }
      } catch (error) {
        console.error('Erro ao iniciar autorização:', error)
        this.$toast.error('Erro ao iniciar autorização')
      } finally {
        this.loading = false
      }
    },
    
    async testConnection() {
      if (!this.currentIntegration) return
      
      this.loading = true
      try {
        const result = await this.testConnection(this.currentIntegration.id)
        
        if (result.success) {
          this.$toast.success('Conexão testada com sucesso')
        }
      } catch (error) {
        console.error('Erro ao testar conexão:', error)
        this.$toast.error('Erro ao testar conexão')
      } finally {
        this.loading = false
      }
    },
    
    async refreshToken() {
      if (!this.currentIntegration) return
      
      this.loading = true
      try {
        const result = await this.refreshToken(this.currentIntegration.id)
        
        if (result.success) {
          this.$toast.success('Token renovado com sucesso')
          await this.loadData()
        }
      } catch (error) {
        console.error('Erro ao renovar token:', error)
        this.$toast.error('Erro ao renovar token')
      } finally {
        this.loading = false
      }
    },
    
    async deleteIntegration() {
      if (!this.currentIntegration) return
      
      if (!confirm('Tem certeza que deseja remover a integração com Google Calendar?')) {
        return
      }
      
      this.loading = true
      try {
        const result = await this.deleteIntegration(this.currentIntegration.id)
        
        if (result.success) {
          this.$toast.success('Integração removida com sucesso')
          await this.loadData()
          await this.checkStatus()
        }
      } catch (error) {
        console.error('Erro ao remover integração:', error)
        this.$toast.error('Erro ao remover integração')
      } finally {
        this.loading = false
      }
    },
    
    async updateSyncEnabled() {
      if (!this.currentIntegration) return
      
      try {
        await this.updateIntegration({
          id: this.currentIntegration.id,
          data: { sync_enabled: this.currentIntegration.sync_enabled }
        })
        
        this.$toast.success('Configuração atualizada')
      } catch (error) {
        console.error('Erro ao atualizar configuração:', error)
        this.$toast.error('Erro ao atualizar configuração')
      }
    },
    
    async syncAll() {
      this.loading = true
      try {
        const result = await this.syncAll()
        
        if (result.success) {
          this.$toast.success('Sincronização global iniciada')
          await this.loadData()
        }
      } catch (error) {
        console.error('Erro ao sincronizar:', error)
        this.$toast.error('Erro ao sincronizar')
      } finally {
        this.loading = false
      }
    },
    
    async loadSyncLogs() {
      await this.fetchSyncLogs()
    },
    
    resetForm() {
      this.form = {
        calendar_id: 'primary',
        sync_enabled: true,
        sync_direction: 'bidirectional',
        notify_on_create: true,
        notify_on_update: true,
        notify_on_delete: true
      }
    },
    
    formatDateTime,
    
    getSyncDirectionColor(direction) {
      const colors = {
        'bidirectional': 'primary',
        'to_google': 'success',
        'from_google': 'info'
      }
      return colors[direction] || 'grey'
    },
    
    getSyncDirectionText(direction) {
      const texts = {
        'bidirectional': 'Bidirecional',
        'to_google': 'Para Google',
        'from_google': 'Do Google'
      }
      return texts[direction] || direction
    },
    
    getSyncStatusColor(status) {
      const colors = {
        'success': 'success',
        'error': 'error',
        'partial': 'warning'
      }
      return colors[status] || 'grey'
    },
    
    getSyncStatusText(status) {
      const texts = {
        'success': 'Sucesso',
        'error': 'Erro',
        'partial': 'Parcial'
      }
      return texts[status] || status
    },
    
    getSyncTypeText(type) {
      const texts = {
        'full': 'Completa',
        'incremental': 'Incremental',
        'manual': 'Manual',
        'automatic': 'Automática'
      }
      return texts[type] || type
    }
  }
}
</script>

<style scoped>
.gap-4 {
  gap: 16px;
}
</style>

