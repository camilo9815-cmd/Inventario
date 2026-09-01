<template>
  <div class="container-fluid">
    <div class="card mb-3">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h4 class="mb-0">{{ idVenta ? 'Editar venta' : 'Crear nueva venta' }}</h4>
        <button
          class="btn btn-outline-secondary"
          type="button"
          @click="emit('consulta')"
        >
          Consultar ventas
        </button>
      </div>

      <div class="card-body">
        <div class="row">
          <div class="col-md-5 mb-3">
            <label class="form-label">Cliente</label>
            <select
              v-model="venta.id_cliente"
              class="form-select"
            >
              <option :value="null">Consumidor final</option>
              <option
                v-for="cliente in clientes"
                :key="cliente.id_cliente"
                :value="cliente.id_cliente"
              >
                {{ cliente.nombre }}
              </option>
            </select>
          </div>

          <div class="col-md-3 mb-3">
            <label class="form-label">Factura</label>
            <input
              v-model="venta.factura"
              class="form-control"
            >
          </div>

          <div class="col-md-3 mb-3">
            <label class="form-label">Medio Pago</label>
            <select
              v-model="venta.id_medio_pago"
              class="form-select"
            >
              <option :value="null">Seleccione...</option>
              <option
                v-for="medio in mediosPago"
                :key="medio.id_medio_pago"
                :value="medio.id_medio_pago"
              >
                {{ medio.nombre }}
              </option>
            </select>
          </div>

          <div
            v-if="venta.id_medio_pago === 5"
            class="col-md-4 mb-3"
          >
            <label class="form-label">Fecha de Vencimiento *</label>
            <input
              v-model="venta.fecha_vencimiento"
              class="form-control"
              type="date"
              required
            >
          </div>

          <div class="col-md-12">
            <label class="form-label">Observacion</label>
            <textarea
              v-model="venta.observacion"
              rows="2"
              class="form-control"
            ></textarea>
          </div>
        </div>
      </div>
    </div>

    <ProductoSelector @productoSeleccionado="agregarProducto" />

    <div class="card mt-3">
      <div class="card-header">
        <strong>Detalle</strong>
      </div>

      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Codigo</th>
              <th>Producto</th>
              <th width="115">Stock</th>
              <th width="120">Cantidad</th>
              <th width="155">Precio</th>
              <th width="120">IVA %</th>
              <th class="text-end">Base</th>
              <th class="text-end">IVA</th>
              <th class="text-end">Total</th>
              <th width="70"></th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="venta.detalle.length === 0">
              <td colspan="10">Agregue productos a la venta.</td>
            </tr>

            <tr
              v-for="(item, index) in venta.detalle"
              :key="item.id_producto"
            >
              <td>{{ item.codigo }}</td>
              <td>{{ item.nombre }}</td>
              <td>{{ item.stock_actual }}</td>
              <td>
                <input
                  v-model.number="item.cantidad"
                  class="form-control"
                  type="number"
                  min="1"
                  step="0.01"
                  @input="calcular(item)"
                >
              </td>
              <td>
                <input
                  v-model.number="item.precio_unitario"
                  class="form-control"
                  type="number"
                  min="0"
                  step="0.01"
                  @input="calcular(item)"
                >
              </td>
              <td>
                <input
                  v-model.number="item.porcentaje_iva"
                  class="form-control"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  @input="calcular(item)"
                >
              </td>
              <td class="text-end">{{ formato(item.base) }}</td>
              <td class="text-end">{{ formato(item.iva) }}</td>
              <td class="text-end fw-bold">{{ formato(item.total) }}</td>
              <td>
                <button
                  class="btn btn-danger btn-sm"
                  type="button"
                  @click="eliminar(index)"
                >
                  X
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body">
        <div class="row justify-content-end">
          <div class="col-md-4">
            <table class="table table-sm">
              <tbody>
                <tr>
                  <th>Subtotal</th>
                  <td class="text-end">{{ formato(subtotal) }}</td>
                </tr>
                <tr>
                  <th>IVA</th>
                  <td class="text-end">{{ formato(iva) }}</td>
                </tr>
                <tr>
                  <th>Total</th>
                  <td class="text-end fw-bold">{{ formato(total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-3 text-end">
      <button
        class="btn btn-secondary me-2"
        type="button"
        @click="cancelar"
      >
        Cancelar
      </button>
      <button
        class="btn btn-success"
        type="button"
        :disabled="guardando"
        @click="guardarVenta"
      >
        {{ idVenta ? 'Actualizar Venta' : 'Guardar Venta' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import ProductoSelector from '../components/ProductoSelector.vue'
import api from '../services/api.js'

const emit = defineEmits(['consulta'])
const props = defineProps({
  idVenta: {
    type: Number,
    default: null,
  },
})

const clientes = ref([])
const mediosPago = ref([])
const guardando = ref(false)

const venta = reactive({
  id_cliente: null,
  factura: '',
  id_medio_pago: null,
  fecha_vencimiento: null,
  observacion: '',
  detalle: [],
})

const subtotal = computed(() => venta.detalle.reduce((total, item) => total + Number(item.base), 0))
const iva = computed(() => venta.detalle.reduce((total, item) => total + Number(item.iva), 0))
const total = computed(() => venta.detalle.reduce((total, item) => total + Number(item.total), 0))

function agregarProducto(producto) {
  const existente = venta.detalle.find((item) => item.id_producto === producto.id_producto)

  if (existente) {
    existente.cantidad += 1
    calcular(existente)
    return
  }

  const item = {
    id_producto: producto.id_producto,
    codigo: producto.codigo,
    nombre: producto.nombre,
    stock_actual: producto.stock_actual ?? 0,
    cantidad: 1,
    precio_unitario: Number(producto.precio_venta_sugerido ?? 0),
    porcentaje_iva: 19,
    base: 0,
    iva: 0,
    total: 0,
  }

  calcular(item)
  venta.detalle.push(item)
}

function calcular(item) {
  item.base = Number(item.cantidad || 0) * Number(item.precio_unitario || 0)
  item.iva = item.base * (Number(item.porcentaje_iva || 0) / 100)
  item.total = item.base + item.iva
}

function eliminar(index) {
  venta.detalle.splice(index, 1)
}

function formato(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(valor ?? 0))
}

async function cargarClientes() {
  const response = await api.get('/clientes')
  clientes.value = response.data
}

async function cargarMediosPago() {
  const response = await api.get('/medios-pago')
  mediosPago.value = response.data
}

async function guardarVenta() {
  if (!venta.id_medio_pago) {
    alert('Seleccione un medio de pago.')
    return
  }

  if (venta.id_medio_pago === 5 && !venta.fecha_vencimiento) {
    alert('Debe especificar una fecha de vencimiento para ventas a crédito.')
    return
  }

  if (venta.detalle.length === 0) {
    alert('Debe agregar al menos un producto.')
    return
  }

  const sinStock = !props.idVenta && venta.detalle.find(
    (item) => Number(item.cantidad) > Number(item.stock_actual)
  )

  if (sinStock) {
    alert(`Stock insuficiente para ${sinStock.nombre}.`)
    return
  }

  guardando.value = true

  try {
    if (props.idVenta) {
      await api.put(`/ventas/${props.idVenta}`, venta)
      alert('Venta actualizada correctamente.')
      emit('consulta')
    } else {
      await api.post('/ventas', venta)
      alert('Venta registrada correctamente.')
      limpiarFormulario()
    }
  } catch (err) {
    alert(err.response?.data?.detail ?? 'Error al registrar la venta.')
  } finally {
    guardando.value = false
  }
}

async function cargarVenta() {
  if (!props.idVenta) return

  const response = await api.get(`/ventas/${props.idVenta}`)
  const datos = response.data
  venta.id_cliente = datos.id_cliente
  venta.factura = datos.factura ?? ''
  venta.id_medio_pago = datos.id_medio_pago
  venta.fecha_vencimiento = datos.fecha_vencimiento ? datos.fecha_vencimiento.substring(0, 10) : null
  venta.observacion = datos.observacion ?? ''
  venta.detalle = datos.detalle.map((item) => ({
    ...item,
    stock_actual: Number(item.cantidad),
    porcentaje_iva: Number(item.base) > 0
      ? (Number(item.iva) / Number(item.base)) * 100
      : 0,
  }))
}

function cancelar() {
  if (props.idVenta) {
    emit('consulta')
  } else {
    limpiarFormulario()
  }
}

function limpiarFormulario() {
  venta.id_cliente = null
  venta.factura = ''
  venta.id_medio_pago = null
  venta.fecha_vencimiento = null
  venta.observacion = ''
  venta.detalle = []
}

onMounted(() => {
  cargarClientes()
  cargarMediosPago()
  cargarVenta()
})
</script>
