<template>
  <div
    v-if="venta"
    class="container-fluid"
  >
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Venta #{{ venta.id_venta }}</h4>

        <div>
          <button
            class="btn btn-primary me-2"
            type="button"
            @click="imprimir"
          >
            Imprimir
          </button>

          <button
            class="btn btn-secondary"
            type="button"
            @click="emit('volver')"
          >
            Volver
          </button>
        </div>
      </div>

      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-3">
            <strong>Cliente</strong>
            <div>{{ venta.cliente }}</div>
          </div>

          <div class="col-md-3">
            <strong>Factura</strong>
            <div>{{ venta.factura }}</div>
          </div>

          <div class="col-md-3">
            <strong>Fecha</strong>
            <div>{{ formatearFecha(venta.fecha) }}</div>
          </div>

          <div class="col-md-3">
            <strong>Medio Pago</strong>
            <div>{{ venta.medio_pago }}</div>
          </div>
        </div>

        <table class="table table-bordered table-hover">
          <thead class="table-light">
            <tr>
              <th>Codigo</th>
              <th>Producto</th>
              <th class="text-center">Cantidad</th>
              <th class="text-end">Precio</th>
              <th class="text-end">Base</th>
              <th class="text-end">IVA</th>
              <th class="text-end">Total</th>
              <th class="text-end">Utilidad</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="item in venta.detalle"
              :key="item.id_detalle_venta"
            >
              <td>{{ item.codigo }}</td>
              <td>{{ item.nombre }}</td>
              <td class="text-center">{{ item.cantidad }}</td>
              <td class="text-end">{{ formato(item.precio_unitario) }}</td>
              <td class="text-end">{{ formato(item.base) }}</td>
              <td class="text-end">{{ formato(item.iva) }}</td>
              <td class="text-end fw-bold">{{ formato(item.total) }}</td>
              <td class="text-end">{{ formato(item.utilidad_bruta) }}</td>
            </tr>
          </tbody>
        </table>

        <div class="row justify-content-end">
          <div class="col-md-4">
            <table class="table">
              <tbody>
                <tr>
                  <th>Subtotal</th>
                  <td class="text-end">{{ formato(venta.subtotal) }}</td>
                </tr>
                <tr>
                  <th>IVA</th>
                  <td class="text-end">{{ formato(venta.iva) }}</td>
                </tr>
                <tr>
                  <th>Total</th>
                  <td class="text-end fw-bold">{{ formato(venta.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    v-else
    class="text-center mt-5"
  >
    Cargando venta...
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import api from '../services/api.js'

const props = defineProps({
  idVenta: Number,
})

const emit = defineEmits(['volver'])

const venta = ref(null)

onMounted(async () => {
  const response = await api.get(`/ventas/${props.idVenta}`)
  venta.value = response.data
})

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

async function imprimir() {
  try {
    const response = await api.get(`/ventas/${props.idVenta}/pdf`, {
      responseType: 'blob',
    })

    const archivo = window.URL.createObjectURL(new Blob([response.data], {
      type: 'application/pdf',
    }))

    window.open(archivo)
  } catch {
    alert('No fue posible generar el PDF.')
  }
}
</script>
