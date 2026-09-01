<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Directorio comercial</p>
        <h2>Clientes</h2>
      </div>
      <button
        class="btn btn-primary"
        type="button"
        @click="abrirFormulario()"
      >
        Nuevo cliente
      </button>
    </div>

    <div class="row mb-3">
      <div class="col-md-8">
        <input
          v-model.trim="busqueda"
          class="form-control"
          type="search"
          placeholder="Buscar por nombre, documento, teléfono o correo"
        >
      </div>
      <div class="col-md-4 d-flex align-items-center">
        <label class="form-check mb-0">
          <input
            v-model="mostrarInactivos"
            class="form-check-input"
            type="checkbox"
            @change="cargarClientes"
          >
          <span class="form-check-label">Mostrar inactivos</span>
        </label>
      </div>
    </div>

    <div
      v-if="error"
      class="alert alert-danger"
    >
      {{ error }}
    </div>

    <div class="table-responsive">
      <table class="table table-hover align-middle">
        <thead>
          <tr>
            <th>Documento</th>
            <th>Nombre</th>
            <th>Teléfono</th>
            <th>Correo</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="cargando">
            <td colspan="6">Cargando clientes...</td>
          </tr>
          <tr v-else-if="clientesFiltrados.length === 0">
            <td colspan="6">No se encontraron clientes.</td>
          </tr>
          <tr
            v-for="cliente in clientesFiltrados"
            v-else
            :key="cliente.id_cliente"
          >
            <td>{{ cliente.documento || '—' }}</td>
            <td class="fw-semibold">{{ cliente.nombre }}</td>
            <td>{{ cliente.telefono || '—' }}</td>
            <td>{{ cliente.correo || '—' }}</td>
            <td>
              <span :class="['status-badge', cliente.activo ? 'status-ok' : 'status-muted']">
                {{ cliente.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button
                class="btn btn-outline-primary btn-sm me-2"
                type="button"
                @click="abrirFormulario(cliente)"
              >
                Editar
              </button>
              <button
                v-if="cliente.activo"
                class="btn btn-outline-danger btn-sm"
                type="button"
                @click="desactivar(cliente)"
              >
                Desactivar
              </button>
              <button
                v-else
                class="btn btn-outline-success btn-sm"
                type="button"
                @click="activar(cliente)"
              >
                Activar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <div
    v-if="formularioVisible"
    class="modal-backdrop-custom"
    @click.self="cerrarFormulario"
  >
    <section class="modal-card">
      <div class="panel-header">
        <h3>{{ formulario.id_cliente ? 'Editar cliente' : 'Nuevo cliente' }}</h3>
        <button
          class="btn-close"
          type="button"
          aria-label="Cerrar"
          @click="cerrarFormulario"
        ></button>
      </div>

      <form @submit.prevent="guardar">
        <div class="row">
          <div class="col-md-5 mb-3">
            <label class="form-label">Documento</label>
            <input
              v-model.trim="formulario.documento"
              class="form-control"
              maxlength="30"
            >
          </div>
          <div class="col-md-7 mb-3">
            <label class="form-label">Nombre *</label>
            <input
              v-model.trim="formulario.nombre"
              class="form-control"
              maxlength="200"
              required
            >
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">Teléfono</label>
            <input
              v-model.trim="formulario.telefono"
              class="form-control"
              maxlength="50"
            >
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">Correo</label>
            <input
              v-model.trim="formulario.correo"
              class="form-control"
              type="email"
              maxlength="150"
            >
          </div>
          <div
            v-if="formulario.id_cliente"
            class="col-12 mb-3"
          >
            <label class="form-check">
              <input
                v-model="formulario.activo"
                class="form-check-input"
                type="checkbox"
              >
              <span class="form-check-label">Cliente activo</span>
            </label>
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2">
          <button
            class="btn btn-secondary"
            type="button"
            @click="cerrarFormulario"
          >
            Cancelar
          </button>
          <button
            class="btn btn-success"
            type="submit"
            :disabled="guardando"
          >
            {{ guardando ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '../services/api.js'

const clientes = ref([])
const busqueda = ref('')
const mostrarInactivos = ref(false)
const cargando = ref(false)
const guardando = ref(false)
const formularioVisible = ref(false)
const error = ref('')

const formulario = reactive({
  id_cliente: null,
  documento: '',
  nombre: '',
  telefono: '',
  correo: '',
  activo: true,
})

const clientesFiltrados = computed(() => {
  const texto = busqueda.value.toLocaleLowerCase('es')
  if (!texto) return clientes.value

  return clientes.value.filter((cliente) => [
    cliente.documento,
    cliente.nombre,
    cliente.telefono,
    cliente.correo,
  ].some((valor) => String(valor ?? '').toLocaleLowerCase('es').includes(texto)))
})

async function cargarClientes() {
  cargando.value = true
  error.value = ''
  try {
    const response = await api.get('/clientes', {
      params: { incluir_inactivos: mostrarInactivos.value },
    })
    clientes.value = response.data
  } catch {
    error.value = 'No fue posible cargar los clientes.'
  } finally {
    cargando.value = false
  }
}

function abrirFormulario(cliente = null) {
  formulario.id_cliente = cliente?.id_cliente ?? null
  formulario.documento = cliente?.documento ?? ''
  formulario.nombre = cliente?.nombre ?? ''
  formulario.telefono = cliente?.telefono ?? ''
  formulario.correo = cliente?.correo ?? ''
  formulario.activo = cliente?.activo ?? true
  formularioVisible.value = true
}

function cerrarFormulario() {
  formularioVisible.value = false
}

function payload() {
  return {
    documento: formulario.documento || null,
    nombre: formulario.nombre,
    telefono: formulario.telefono || null,
    correo: formulario.correo || null,
    activo: formulario.activo,
  }
}

async function guardar() {
  guardando.value = true
  try {
    if (formulario.id_cliente) {
      await api.put(`/clientes/${formulario.id_cliente}`, payload())
    } else {
      await api.post('/clientes', payload())
    }
    cerrarFormulario()
    await cargarClientes()
  } catch (err) {
    alert(err.response?.data?.detail ?? 'No fue posible guardar el cliente.')
  } finally {
    guardando.value = false
  }
}

async function desactivar(cliente) {
  if (!confirm(`¿Desactivar a ${cliente.nombre}?`)) return
  try {
    await api.delete(`/clientes/${cliente.id_cliente}`)
    await cargarClientes()
  } catch (err) {
    alert(err.response?.data?.detail ?? 'No fue posible desactivar el cliente.')
  }
}

async function activar(cliente) {
  try {
    await api.put(`/clientes/${cliente.id_cliente}`, {
      documento: cliente.documento,
      nombre: cliente.nombre,
      telefono: cliente.telefono,
      correo: cliente.correo,
      activo: true,
    })
    await cargarClientes()
  } catch (err) {
    alert(err.response?.data?.detail ?? 'No fue posible activar el cliente.')
  }
}

onMounted(cargarClientes)
</script>
