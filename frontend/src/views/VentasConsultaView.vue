<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Ventas</p>
        <h2>Consulta de ventas</h2>
      </div>

      <button
        class="btn btn-primary"
        type="button"
        @click="emit('nueva')"
      >
        Nueva venta
      </button>
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
            <th>#</th>
            <th>Fecha</th>
            <th>Factura</th>
            <th>Cliente</th>
            <th>Medio Pago</th>
            <th class="text-end">Total</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>
          <tr v-if="cargando">
            <td colspan="7">Cargando ventas...</td>
          </tr>

          <tr v-else-if="ventas.length === 0">
            <td colspan="7">No existen ventas registradas.</td>
          </tr>

          <tr
            v-for="venta in ventas"
            v-else
            :key="venta.id_venta"
          >
            <td>{{ venta.id_venta }}</td>
            <td>{{ formatearFecha(venta.fecha) }}</td>
            <td>{{ venta.factura }}</td>
            <td>{{ venta.cliente }}</td>
            <td>{{ venta.medio_pago }}</td>
            <td class="text-end">{{ formato(venta.total) }}</td>
            <td>
              <button
                class="btn btn-primary btn-sm me-2"
                type="button"
                @click="emit('ver', venta.id_venta)"
              >
                Ver
              </button>
              <button
                class="btn btn-outline-primary btn-sm me-2"
                type="button"
                @click="emit('editar', venta.id_venta)"
              >
                Editar
              </button>
              <button
                class="btn btn-outline-danger btn-sm"
                type="button"
                @click="eliminarVenta(venta)"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import api from '../services/api.js'

const emit = defineEmits(['ver', 'nueva', 'editar'])

const ventas = ref([])
const cargando = ref(false)
const error = ref('')

async function cargarVentas() {
  cargando.value = true
  error.value = ''

  try {
    const response = await api.get('/ventas')
    ventas.value = response.data
  } catch {
    error.value = 'No fue posible cargar las ventas.'
  } finally {
    cargando.value = false
  }
}

async function eliminarVenta(venta) {
  if (!confirm(`¿Eliminar la venta #${venta.id_venta}? El inventario vendido será reintegrado.`)) {
    return
  }

  try {
    await api.delete(`/ventas/${venta.id_venta}`)
    await cargarVentas()
  } catch (err) {
    alert(err.response?.data?.detail ?? 'No fue posible eliminar la venta.')
  }
}

function formato(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(valor ?? 0))
}

function formatearFecha(fecha) {
  return new Date(fecha).toLocaleDateString('es-CO')
}

onMounted(cargarVentas)
</script>
