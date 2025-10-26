<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height">
        <v-row align="center" justify="center" class="fill-height">
          <v-col cols="12" sm="8" md="6" lg="4" xl="3">
            <v-card class="elevation-12">
              <v-card-title class="text-center pa-8">
                <div class="d-flex flex-column align-center">
                  <v-avatar size="64" class="mb-4">
                    <v-img src="/icons/logo.png" alt="Logo" />
                  </v-avatar>
                  <h1 class="text-h4 font-weight-bold text-primary">
                    Secretaria Virtual
                  </h1>
                  <p class="text-subtitle1 text-grey-darken-1 mt-2">
                    Appointment and Management System
                  </p>
                </div>
              </v-card-title>

              <v-card-text class="pa-8">
                <v-form ref="form" v-model="valid" @submit.prevent="handleLogin">
                  <v-text-field
                    v-model="form.email"
                    :rules="emailRules"
                    label="E-mail"
                    type="email"
                    prepend-inner-icon="mdi-email"
                    variant="outlined"
                    required
                    :disabled="loading"
                    class="mb-4"
                  />

                  <v-text-field
                    v-model="form.password"
                    :rules="passwordRules"
                    label="Senha"
                    :type="showPassword ? 'text' : 'password'"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    variant="outlined"
                    required
                    :disabled="loading"
                    @click:append-inner="showPassword = !showPassword"
                    class="mb-4"
                  />

                  <v-checkbox
                    v-model="form.rememberMe"
                    label="Lembrar de mim"
                    :disabled="loading"
                    class="mb-4"
                  />

                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    :loading="loading"
                    :disabled="!valid || loading"
                    class="mb-4"
                  >
                    Entrar
                  </v-btn>

                  <div class="text-center">
                    <v-btn
                      variant="text"
                      color="primary"
                      @click="forgotPassword"
                      :disabled="loading"
                    >
                      Esqueci minha senha
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>

              <v-card-actions class="pa-8 pt-0">
                <v-divider class="mb-4" />
                
                <div class="text-center w-100">
                  <p class="text-body2 text-grey-darken-1 mb-4">
                    Ou entre com
                  </p>
                  
                  <div class="d-flex justify-center gap-2">
                    <v-btn
                      icon
                      variant="outlined"
                      color="red"
                      @click="loginWithGoogle"
                      :disabled="loading"
                    >
                      <v-icon>mdi-google</v-icon>
                    </v-btn>
                    
                    <v-btn
                      icon
                      variant="outlined"
                      color="blue"
                      @click="loginWithFacebook"
                      :disabled="loading"
                    >
                      <v-icon>mdi-facebook</v-icon>
                    </v-btn>
                    
                    <v-btn
                      icon
                      variant="outlined"
                      color="grey-darken-1"
                      @click="loginWithMicrosoft"
                      :disabled="loading"
                    >
                      <v-icon>mdi-microsoft</v-icon>
                    </v-btn>
                  </div>
                </div>
              </v-card-actions>
            </v-card>

            <div class="text-center mt-6">
              <p class="text-body2 text-grey-darken-1">
                Don't have an account?
                <v-btn
                  variant="text"
                  color="primary"
                  @click="register"
                  :disabled="loading"
                >
                  Cadastre-se
                </v-btn>
              </p>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      valid: false,
      loading: false,
      showPassword: false,
      form: {
        email: '',
        password: '',
        rememberMe: false
      },
      emailRules: [
        v => !!v || 'Email is required',
        v => /.+@.+\..+/.test(v) || 'Email must be valid'
      ],
      passwordRules: [
        v => !!v || 'Password is required',
        v => v.length >= 6 || 'Password must have at least 6 characters'
      ]
    }
  },
  methods: {
    ...mapActions('auth', ['login']),
    
    async handleLogin() {
      if (!this.valid) return
      
      this.loading = true
      
      try {
        const result = await this.login(this.form)
        
        if (result.success) {
          this.$router.push('/dashboard')
        } else {
          this.$toast.error(result.error || 'Erro ao fazer login')
        }
      } catch (error) {
        this.$toast.error('Erro inesperado ao fazer login')
        console.error('Erro no login:', error)
      } finally {
        this.loading = false
      }
    },
    
    forgotPassword() {
      this.$router.push('/forgot-password')
    },
    
    register() {
      this.$router.push('/register')
    },
    
    loginWithGoogle() {
      // Implementar login com Google
      this.$toast.info('Login com Google em desenvolvimento')
    },
    
    loginWithFacebook() {
      // Implementar login com Facebook
      this.$toast.info('Login com Facebook em desenvolvimento')
    },
    
    loginWithMicrosoft() {
      // Implementar login com Microsoft
      this.$toast.info('Login com Microsoft em desenvolvimento')
    }
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.gap-2 {
  gap: 8px;
}
</style>

