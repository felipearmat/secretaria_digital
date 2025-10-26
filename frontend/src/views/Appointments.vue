<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary mb-2">
              Appointments
            </h1>
            <p class="text-subtitle1 text-grey-darken-1">
              Manage all your appointments
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
              prepend-icon="mdi-filter"
              @click="showFilters = !showFilters"
            >
              Filters
            </v-btn>
            
            <v-btn
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="loadAppointments"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-expand-transition>
      <v-card v-show="showFilters" class="mb-6">
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.search"
                label="Search"
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
                @update:model-value="loadAppointments"
              />
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.actor"
                label="Actor"
                :items="actorsOptions"
                variant="outlined"
                clearable
                @update:model-value="loadAppointments"
              />
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.service"
                label="Service"
                :items="servicesOptions"
                variant="outlined"
                clearable
                @update:model-value="loadAppointments"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="filters.start_date"
                label="Start Date"
                type="date"
                variant="outlined"
                @update:model-value="loadAppointments"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="filters.end_date"
                label="End Date"
                type="date"
                variant="outlined"
                @update:model-value="loadAppointments"
              />
            </v-col>
          </v-row>
          
          <div class="d-flex justify-end gap-2 mt-4">
            <v-btn
              variant="outlined"
              @click="clearFilters"
            >
              Clear Filters
            </v-btn>
            
            <v-btn
              color="primary"
              @click="loadAppointments"
            >
              Apply Filters
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- Appointments List -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="appointments"
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
        
        <!-- Date/Time -->
        <template v-slot:item.start_time="{ item }">
          <div>
            <div class="text-body2 font-weight-medium">
              {{ formatDate(item.start_time) }}
            </div>
            <div class="text-caption text-grey-darken-1">
              {{ formatTime(item.start_time) }}
            </div>
          </div>
        </template>
        
        <!-- Client -->
        <template v-slot:item.client_name="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-img
                v-if="item.client_avatar"
                :src="item.client_avatar"
                :alt="item.client_name"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-body2 font-weight-medium">
                {{ item.client_name }}
              </div>
              <div class="text-caption text-grey-darken-1">
                {{ item.client_email }}
              </div>
            </div>
          </div>
        </template>
        
        <!-- Actor -->
        <template v-slot:item.actor_name="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-img
                v-if="item.actor_avatar"
                :src="item.actor_avatar"
                :alt="item.actor_name"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-body2 font-weight-medium">
                {{ item.actor_name }}
              </div>
              <div class="text-caption text-grey-darken-1">
                {{ item.service_name }}
              </div>
            </div>
          </div>
        </template>
        
        <!-- Price -->
        <template v-slot:item.final_price="{ item }">
          <div class="text-body2 font-weight-medium">
            {{ formatCurrency(item.final_price) }}
          </div>
        </template>
        
        <!-- Actions -->
        <template v-slot:item.actions="{ item }">
          <div class="d-flex align-center gap-2">
            <v-btn
              icon
              size="small"
              variant="text"
              @click="viewAppointment(item)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            
            <v-btn
              icon
              size="small"
              variant="text"
              @click="editAppointment(item)"
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
                  v-if="item.status === 'pending'"
                  @click="confirmAppointment(item)"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-check</v-icon>
                  </template>
                  <v-list-item-title>Confirm</v-list-item-title>
                </v-list-item>
                
                <v-list-item
                  v-if="item.status === 'pending' || item.status === 'confirmed'"
                  @click="cancelAppointment(item)"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-close</v-icon>
                  </template>
                  <v-list-item-title>Cancel</v-list-item-title>
                </v-list-item>
                
                <v-list-item
                  v-if="item.status === 'pending'"
                  @click="rejectAppointment(item)"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-close-circle</v-icon>
                  </template>
                  <v-list-item-title>Reject</v-list-item-title>
                </v-list-item>
                
                <v-divider />
                
                <v-list-item
                  @click="deleteAppointment(item)"
                  class="text-error"
                >
                  <template v-slot:prepend>
                    <v-icon color="error">mdi-delete</v-icon>
                  </template>
                  <v-list-item-title>Delete</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Confirmation Dialog -->
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
            Cancel
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
  name: 'Appointments',
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
        actor: '',
        service: '',
        start_date: '',
        end_date: ''
      },
      statusOptions: [
        { title: 'Pending', value: 'pending' },
        { title: 'Confirmed', value: 'confirmed' },
        { title: 'Cancelled', value: 'cancelled' },
        { title: 'Completed', value: 'completed' }
      ],
      actorsOptions: [],
      servicesOptions: [],
      headers: [
        { title: 'Status', key: 'status', sortable: false },
        { title: 'Date/Time', key: 'start_time', sortable: true },
        { title: 'Client', key: 'client_name', sortable: false },
        { title: 'Actor/Service', key: 'actor_name', sortable: false },
        { title: 'Price', key: 'final_price', sortable: true },
        { title: 'Actions', key: 'actions', sortable: false }
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
    ...mapState('appointments', ['appointments', 'pagination']),
    ...mapGetters('appointments', ['loading'])
  },
  async mounted() {
    this.debouncedSearch = debounce(this.loadAppointments, 500)
    await this.loadAppointments()
    await this.loadOptions()
  },
  methods: {
    ...mapActions('appointments', [
      'fetchAppointments',
      'confirmAppointment',
      'cancelAppointment',
      'deleteAppointment'
    ]),
    
    async loadAppointments() {
      this.loading = true
      
      try {
        const params = {
          page: this.currentPage,
          page_size: this.itemsPerPage,
          ...this.filters
        }
        
        // Remove empty parameters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null) {
            delete params[key]
          }
        })
        
        const result = await this.fetchAppointments(params)
        
        if (result.success) {
          this.totalItems = this.pagination.total
        }
      } catch (error) {
        console.error('Error loading appointments:', error)
        this.$toast.error('Error loading appointments')
      } finally {
        this.loading = false
      }
    },
    
    async loadOptions() {
      // Load options for filters
      // In production, would come from API
      this.actorsOptions = [
        { title: 'João Silva', value: 1 },
        { title: 'Maria Santos', value: 2 },
        { title: 'Pedro Costa', value: 3 }
      ]
      
      this.servicesOptions = [
        { title: 'Medical Consultation', value: 1 },
        { title: 'Blood Test', value: 2 },
        { title: 'Ultrasound', value: 3 }
      ]
    },
    
    onPageChange(page) {
      this.currentPage = page
      this.loadAppointments()
    },
    
    onItemsPerPageChange(itemsPerPage) {
      this.itemsPerPage = itemsPerPage
      this.currentPage = 1
      this.loadAppointments()
    },
    
    clearFilters() {
      this.filters = {
        search: '',
        status: '',
        actor: '',
        service: '',
        start_date: '',
        end_date: ''
      }
      this.loadAppointments()
    },
    
    viewAppointment(item) {
      this.$router.push(`/appointments/${item.id}`)
    },
    
    editAppointment(item) {
      this.$router.push(`/appointments/${item.id}/edit`)
    },
    
    confirmAppointment(item) {
      this.confirmDialog = {
        show: true,
        title: 'Confirm Appointment',
        message: `Do you want to confirm the appointment for ${item.client_name}?`,
        confirmText: 'Confirm',
        color: 'success',
        loading: false,
        action: 'confirm',
        item
      }
    },
    
    cancelAppointment(item) {
      this.confirmDialog = {
        show: true,
        title: 'Cancel Appointment',
        message: `Do you want to cancel the appointment for ${item.client_name}?`,
        confirmText: 'Cancel',
        color: 'warning',
        loading: false,
        action: 'cancel',
        item
      }
    },
    
    rejectAppointment(item) {
      this.confirmDialog = {
        show: true,
        title: 'Reject Appointment',
        message: `Do you want to reject the appointment for ${item.client_name}?`,
        confirmText: 'Reject',
        color: 'error',
        loading: false,
        action: 'reject',
        item
      }
    },
    
    deleteAppointment(item) {
      this.confirmDialog = {
        show: true,
        title: 'Delete Appointment',
        message: `Do you want to permanently delete the appointment for ${item.client_name}?`,
        confirmText: 'Delete',
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
            await this.confirmAppointment(item.id)
            this.$toast.success('Appointment confirmed')
            break
            
          case 'cancel':
            await this.cancelAppointment(item.id)
            this.$toast.success('Appointment cancelled')
            break
            
          case 'reject':
            // Implement rejection
            this.$toast.success('Appointment rejected')
            break
            
          case 'delete':
            await this.deleteAppointment(item.id)
            this.$toast.success('Appointment deleted')
            break
        }
        
        this.confirmDialog.show = false
        await this.loadAppointments()
      } catch (error) {
        console.error('Error executing action:', error)
        this.$toast.error('Error executing action')
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
        'pending': 'warning',
        'confirmed': 'success',
        'cancelled': 'error',
        'completed': 'info'
      }
      return colors[status] || 'grey'
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

