<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-copy">
            <img
        :src="logo"
        class="logo-login"
        alt="Farcrop ERP"
    >
        <p class="eyebrow">ERP de inventario Farcrop</p>
        <p>
          Administra productos, existencias, costos e IVA desde una interfaz
          pensada para operación diaria.
        </p>
      </div>

      <form
        class="login-card"
        @submit.prevent="login"
      >
        <div>
          <p class="eyebrow">Acceso seguro</p>
          <h2>Iniciar sesión</h2>
        </div>

        <div
          v-if="error"
          class="alert alert-danger"
          role="alert"
        >
          {{ error }}
        </div>

        <div class="form-group">
          <label for="usuario">Usuario</label>
          <input
            id="usuario"
            v-model="usuario"
            class="form-control"
            autocomplete="username"
            autofocus
          >
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            autocomplete="current-password"
          >
        </div>

        <button
          class="btn btn-primary w-100"
          type="submit"
          :disabled="loading"
        >
          {{ loading ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>
    </section>
  </main>
</template>
<style>
.logo-login{

    width:380px;

    margin-bottom:30px;

    display:block;

}
</style>
<script setup>
import logo from "../assets/logo.png"
import { ref } from 'vue'
import api from '../services/api'

const emit = defineEmits(['authenticated'])

const usuario = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function login() {
  error.value = ''
  loading.value = true

  const formData = new FormData()

  formData.append('username', usuario.value)
  formData.append('password', password.value)

  try {
    const response = await api.post('/login', formData)
    const token = response.data.access_token

    localStorage.setItem('erp_token', token)
    emit('authenticated', token)
  } catch {
    error.value = 'Usuario o contraseña incorrectos.'
  } finally {
    loading.value = false
  }
}
</script>
