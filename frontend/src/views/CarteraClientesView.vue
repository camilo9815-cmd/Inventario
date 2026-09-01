<template>
  <section class="panel">
    <div class="panel-header py-3">
      <div>
        <p class="eyebrow">Cartera y Cobranzas</p>
        <h2>Cartera de Clientes</h2>
      </div>
      <div class="btn-group">
        <button
          class="btn"
          :class="vistaActiva === 'saldos' ? 'btn-primary' : 'btn-outline-primary'"
          @click="vistaActiva = 'saldos'"
        >
          Cuentas por Cobrar
        </button>
        <button
          class="btn"
          :class="vistaActiva === 'recibos' ? 'btn-primary' : 'btn-outline-primary'"
          @click="vistaActiva = 'recibos'"
        >
          Historial de Recibos
        </button>
      </div>
    </div>

    <!-- PANE 1: SALDOS -->
    <div v-show="vistaActiva === 'saldos'">
      <div class="row mb-3">
        <div class="col-md-12">
          <input
            v-model.trim="busqueda"
            class="form-control"
            type="search"
            placeholder="Buscar por cliente o identificación"
          >
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Documento</th>
              <th class="text-end">Ventas Pendientes</th>
              <th class="text-end">Saldo Pendiente</th>
              <th>Vencimiento Próximo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargando">
              <td colspan="6">Cargando saldos de cartera...</td>
            </tr>
            <tr v-else-if="clientesConSaldo.length === 0">
              <td colspan="6">No hay saldos pendientes de cobro.</td>
            </tr>
            <tr
              v-for="cliente in clientesFiltrados"
              :key="cliente.id_cliente"
            >
              <td class="fw-semibold">{{ cliente.nombre }}</td>
              <td>{{ cliente.documento || '—' }}</td>
              <td class="text-end">{{ cliente.ventasCount }}</td>
              <td class="text-end fw-bold text-danger">
                $ {{ formatDecimal(cliente.saldoTotal) }}
              </td>
              <td>
                <span :class="{'text-danger fw-bold': esVencido(cliente.proximoVencimiento)}">
                  {{ formatFecha(cliente.proximoVencimiento) }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-sm btn-success"
                  @click="abrirCobro(cliente)"
                >
                  Registrar Cobro
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PANE 2: RECIBOS -->
    <div v-show="vistaActiva === 'recibos'">
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Número</th>
              <th>Fecha</th>
              <th>Cliente</th>
              <th>Concepto</th>
              <th class="text-end">Total Recibido</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargandoRecibos">
              <td colspan="6">Cargando historial de recibos...</td>
            </tr>
            <tr v-else-if="recibos.length === 0">
              <td colspan="6">No se han registrado recibos de caja.</td>
            </tr>
            <tr
              v-for="recibo in recibos"
              :key="recibo.id_recibo"
            >
              <td class="fw-bold">{{ recibo.numero }}</td>
              <td>{{ formatFechaHora(recibo.fecha) }}</td>
              <td class="fw-semibold">{{ recibo.cliente_nombre }}</td>
              <td>{{ recibo.observacion || 'Abono a facturas' }}</td>
              <td class="text-end fw-bold text-success">
                $ {{ formatDecimal(recibo.total) }}
              </td>
              <td>
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="abrirDetalle(recibo.id_recibo)"
                >
                  Ver Detalle
                </button>

                    <button
                    class="btn btn-outline-danger"
                    @click="eliminarRecibo(recibo)"
                  >
                    Eliminar
                  </button>

              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- MODAL: REGISTRAR COBRO -->
  <div
    v-if="modalCobroVisible"
    class="modal-backdrop-custom"
    @click.self="cerrarCobro"
  >
    <section class="modal-card" style="max-width: 800px;">
      <div class="panel-header">
        <h3>Registrar Recibo de Caja</h3>
        <button class="btn-close" @click="cerrarCobro"></button>
      </div>

      <div class="mb-3">
        <h5>Cliente: <span class="text-primary">{{ clienteSeleccionado?.nombre }}</span></h5>
        <div class="alert alert-secondary py-2 mb-2">
          <strong>Saldo Total Pendiente:</strong> $ {{ formatDecimal(clienteSeleccionado?.saldoTotal) }}
        </div>
      </div>

      <form @submit.prevent="guardarCobro">
        <div class="row mb-3">
          <div class="col-md-6">
            <label class="form-label">Número de Recibo (Opcional)</label>
            <input
              v-model="formularioCobro.numero"
              class="form-control"
              placeholder="Auto-generado"
            >
          </div>
          <div class="col-md-6">
            <label class="form-label">Observación / Concepto</label>
            <input
              v-model="formularioCobro.observacion"
              class="form-control"
              placeholder="p.ej. Cancelación saldo facturas"
            >
          </div>
        </div>

        <h5 class="mt-4 mb-3">Facturas Pendientes</h5>
        <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
          <table class="table table-sm align-middle">
            <thead>
              <tr>
                <th>Factura</th>
                <th>Fecha</th>
                <th>Vencimiento</th>
                <th class="text-end">Total</th>
                <th class="text-end">Saldo</th>
                <th class="text-end" style="width: 150px;">Abonar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="venta in ventasCliente" :key="venta.id_venta">
                <td>{{ venta.factura || ('Venta #' + venta.id_venta) }}</td>
                <td>{{ formatFechaSimple(venta.fecha) }}</td>
                <td>
                  <span :class="{'text-danger': esVencido(venta.fecha_vencimiento)}">
                    {{ formatFechaSimple(venta.fecha_vencimiento) }}
                  </span>
                </td>
                <td class="text-end">$ {{ formatDecimal(venta.total) }}</td>
                <td class="text-end text-danger fw-bold">$ {{ formatDecimal(venta.saldo) }}</td>
                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input
                      v-model.number="venta.montoPagar"
                      type="number"
                      class="form-control text-end"
                      :max="venta.saldo"
                      min="0"
                      step="0.01"
                      @input="calcularTotalCobro"
                    >
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
          <h4>Total a Recibir: <span class="text-success">$ {{ formatDecimal(formularioCobro.total) }}</span></h4>
          <div class="d-flex gap-2">
            <button
              class="btn btn-secondary"
              type="button"
              @click="cerrarCobro"
            >
              Cancelar
            </button>
            <button
              class="btn btn-success"
              type="submit"
              :disabled="guardando || formularioCobro.total <= 0"
            >
              {{ guardando ? 'Registrando...' : 'Registrar Pago' }}
            </button>
          </div>
        </div>
      </form>
    </section>
  </div>

  <!-- MODAL: VER DETALLE RECIBO -->
  <div
    v-if="modalDetalleVisible"
    class="modal-backdrop-custom"
    @click.self="cerrarDetalle"
  >
    <section class="modal-card" style="max-width: 600px;">
      <div class="panel-header">
        <h3>Detalle Recibo de Caja</h3>
        <button class="btn-close" @click="cerrarDetalle"></button>
      </div>

      <div class="row mb-3" v-if="reciboSeleccionado">
        <div class="col-6 mb-2">
          <strong>Número:</strong><br>{{ reciboSeleccionado.numero }}
        </div>
        <div class="col-6 mb-2">
          <strong>Fecha:</strong><br>{{ formatFechaHora(reciboSeleccionado.fecha) }}
        </div>
        <div class="col-6 mb-2">
          <strong>Cliente:</strong><br>{{ reciboSeleccionado.cliente_nombre }}
        </div>
        <div class="col-6 mb-2">
          <strong>Registrado por:</strong><br>{{ reciboSeleccionado.usuario_nombre || 'Sistemas' }}
        </div>
        <div class="col-12 mb-2">
          <strong>Concepto:</strong><br>{{ reciboSeleccionado.observacion || '—' }}
        </div>
      </div>

      <h5 class="mt-4">Facturas Facturadas / Pagadas</h5>
      <ul class="list-group mb-3" v-if="reciboSeleccionado">
        <li
          v-for="det in reciboSeleccionado.detalles"
          :key="det.id_detalle"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>Factura:</strong> {{ det.factura_venta || ('Venta #' + det.id_venta) }}
          </div>
          <span class="badge bg-success fs-6">
            $ {{ formatDecimal(det.valor) }}
          </span>
        </li>
      </ul>

      <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top" v-if="reciboSeleccionado">
        <h4>Total Cobrado:</h4>
        <h3 class="text-success">$ {{ formatDecimal(reciboSeleccionado.total) }}</h3>
      </div>

      <div class="d-flex justify-content-end gap-2 mt-3">
        <button class="btn btn-secondary" @click="cerrarDetalle">Cerrar</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../services/api.js'

const vistaActiva = ref('saldos')
const busqueda = ref('')
const cargando = ref(false)
const cargandoRecibos = ref(false)
const guardando = ref(false)
const error = ref('')

const clientesConSaldo = ref([])
const recibos = ref([])

// Modals
const modalCobroVisible = ref(false)
const modalDetalleVisible = ref(false)
const clienteSeleccionado = ref(null)
const ventasCliente = ref([])
const reciboSeleccionado = ref(null)

const formularioCobro = reactive({
  numero: '',
  observacion: '',
  total: 0
})

const clientesFiltrados = computed(() => {
  const query = busqueda.value.toLowerCase()
  if (!query) return clientesConSaldo.value

  return clientesConSaldo.value.filter(c => 
    c.nombre.toLowerCase().includes(query) || 
    (c.documento && c.documento.includes(query))
  )
})

async function cargarDatos() {
  cargando.value = true
  error.value = ''
  try {
    // Cargar todas las ventas
    const responseVentas = await api.get('/ventas')
    const ventas = responseVentas.data
    console.log(responseVentas.data)
    // Agrupar ventas con saldo > 0 por cliente
    const agrupado = {}
    ventas.forEach(v => {
      const saldo = parseFloat(v.saldo || 0)
      const clienteId = v.id_cliente
      if (saldo > 0 && clienteId) {
        const clienteNom = v.cliente || 'Cliente #' + clienteId
        
        if (!agrupado[clienteId]) {
          agrupado[clienteId] = {
            id_cliente: clienteId,
            nombre: clienteNom,
            documento: '', // se rellenará si es cliente registrado
            saldoTotal: 0,
            ventasCount: 0,
            proximoVencimiento: null,
            ventasLink: []
          }
        }
        
        agrupado[clienteId].saldoTotal += saldo
        agrupado[clienteId].ventasCount++
        agrupado[clienteId].ventasLink.push({
          ...v,
          montoPagar: 0
        })

        if (v.fecha_vencimiento) {
          const fVenc = new Date(v.fecha_vencimiento)
          if (!agrupado[clienteId].proximoVencimiento || fVenc < new Date(agrupado[clienteId].proximoVencimiento)) {
            agrupado[clienteId].proximoVencimiento = v.fecha_vencimiento
          }
        }
      }
    })

    // Cargar lista de clientes para completar datos del documento
    const responseClientes = await api.get('/clientes')
    const clientesList = responseClientes.data

    Object.keys(agrupado).forEach(id => {
      const idNum = parseInt(id)
      const found = clientesList.find(c => c.id_cliente === idNum)
      if (found) {
        agrupado[id].documento = found.documento
      }
    })

    clientesConSaldo.value = Object.values(agrupado)
    
    // Cargar recibos
    await cargarRecibos()
  } catch (err) {
    error.value = 'Error al cargar saldos de cartera.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}

async function cargarRecibos() {
  cargandoRecibos.value = true
  try {
    const res = await api.get('/recibos-caja')
    recibos.value = res.data
  } catch (err) {
    console.error('Error al cargar recibos de caja:', err)
  } finally {
    cargandoRecibos.value = false
  }
}

function abrirCobro(cliente) {
  clienteSeleccionado.value = cliente
  // Clonar las facturas pendientes para este modal
  ventasCliente.value = cliente.ventasLink.map(v => ({ ...v, montoPagar: 0 }))
  formularioCobro.numero = ''
  formularioCobro.observacion = ''
  formularioCobro.total = 0
  modalCobroVisible.value = true
}

function cerrarCobro() {
  modalCobroVisible.value = false
  clienteSeleccionado.value = null
  ventasCliente.value = []
}

function calcularTotalCobro() {
  let sum = 0
  ventasCliente.value.forEach(v => {
    const val = parseFloat(v.montoPagar || 0)
    sum += val
  })
  formularioCobro.total = sum
}

async function guardarCobro() {
  if (formularioCobro.total <= 0) return
  guardando.value = true
  try {
    const payload = {
      numero: formularioCobro.numero || null,
      id_cliente: clienteSeleccionado.value.id_cliente,
      observacion: formularioCobro.observacion || null,
      detalles: ventasCliente.value
        .filter(v => parseFloat(v.montoPagar || 0) > 0)
        .map(v => ({
          id_venta: v.id_venta,
          valor: parseFloat(v.montoPagar)
        }))
    }



    await api.post('/recibos-caja', payload)
    cerrarCobro()
    await cargarDatos()
  } catch (err) {
    alert(err.response?.data?.detail ?? 'No fue posible registrar el recibo de caja.')
  } finally {
    guardando.value = false
  }
}

async function abrirDetalle(idRecibo) {
  try {
    const res = await api.get(`/recibos-caja/${idRecibo}`)
    reciboSeleccionado.value = res.data
    modalDetalleVisible.value = true
  } catch (err) {
    alert('No fue posible cargar el detalle del recibo.')
  }
}

function cerrarDetalle() {
  modalDetalleVisible.value = false
  reciboSeleccionado.value = null
}

// Helpers
function formatDecimal(val) {
  if (val === undefined || val === null) return '0.00'
  return parseFloat(val).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

function formatFecha(val) {
  if (!val) return '—'
  const date = new Date(val)
  return date.toLocaleDateString()
}

function formatFechaHora(val) {
  if (!val) return '—'
  const date = new Date(val)
  return date.toLocaleString()
}

function formatFechaSimple(val) {
  if (!val) return '—'
  return val.substring(0, 10)
}

function esVencido(val) {
  if (!val) return false
  return new Date(val) < new Date().setHours(0,0,0,0)
}

onMounted(cargarDatos)

async function eliminarRecibo(recibo) {

  const confirmar = confirm(
    `¿Está seguro de eliminar el recibo ${recibo.numero}?\n\nEsta acción restaurará los saldos de las facturas pagadas.`
  )

  if (!confirmar) return

  try {

    await api.delete(`/recibos-caja/${recibo.id_recibo}`)

    await cargarDatos()

    alert("Recibo eliminado correctamente.")

  } catch (err) {

    alert(
      err.response?.data?.detail ??
      "No fue posible eliminar el recibo."
    )

  }

}
</script>
