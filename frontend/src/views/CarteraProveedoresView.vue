<template>
  <section class="panel">
    <div class="panel-header py-3">
      <div>
        <p class="eyebrow">Cartera y Cuentas por Pagar</p>
        <h2>Cartera de Proveedores</h2>
      </div>
      <div class="btn-group">
        <button
          class="btn"
          :class="vistaActiva === 'saldos' ? 'btn-primary' : 'btn-outline-primary'"
          @click="vistaActiva = 'saldos'"
        >
          Cuentas por Pagar
        </button>
        <button
          class="btn"
          :class="vistaActiva === 'egresos' ? 'btn-primary' : 'btn-outline-primary'"
          @click="vistaActiva = 'egresos'"
        >
          Historial de Pagos
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
            placeholder="Buscar por proveedor o identificación"
          >
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Proveedor</th>
              <th>NIT / RUT</th>
              <th class="text-end">Compras Pendientes</th>
              <th class="text-end">Saldo Pendiente</th>
              <th>Vencimiento Próximo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargando">
              <td colspan="6">Cargando saldos de proveedores...</td>
            </tr>
            <tr v-else-if="proveedoresConSaldo.length === 0">
              <td colspan="6">No se registran saldos pendientes de pago.</td>
            </tr>
            <tr
              v-for="prov in proveedoresFiltrados"
              :key="prov.id_proveedor"
            >
              <td class="fw-semibold">{{ prov.nombre }}</td>
              <td>{{ prov.nit || '—' }}</td>
              <td class="text-end">{{ prov.comprasCount }}</td>
              <td class="text-end fw-bold text-danger">
                $ {{ formatDecimal(prov.saldoTotal) }}
              </td>
              <td>
                <span :class="{'text-danger fw-bold': esVencido(prov.proximoVencimiento)}">
                  {{ formatFecha(prov.proximoVencimiento) }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-sm btn-success"
                  @click="abrirPago(prov)"
                >
                  Registrar Pago
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PANE 2: EGRESOS -->
    <div v-show="vistaActiva === 'egresos'">
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Número</th>
              <th>Fecha</th>
              <th>Proveedor</th>
              <th>Concepto</th>
              <th class="text-end">Total Pagado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargandoEgresos">
              <td colspan="6">Cargando historial de egresos...</td>
            </tr>
            <tr v-else-if="egresos.length === 0">
              <td colspan="6">No se han registrado comprobantes de egreso.</td>
            </tr>
            <tr
              v-for="egr in egresos"
              :key="egr.id_egreso"
            >
              <td class="fw-bold">{{ egr.numero }}</td>
              <td>{{ formatFechaHora(egr.fecha) }}</td>
              <td class="fw-semibold">{{ egr.proveedor_nombre }}</td>
              <td>{{ egr.observacion || 'Pago a facturas' }}</td>
              <td class="text-end fw-bold text-danger">
                $ {{ formatDecimal(egr.total) }}
              </td>
              <td>
                <button
                  class="btn btn-sm btn-outline-primary"
                  @click="abrirDetalle(egr.id_egreso)"
                >
                  Ver Detalle
                </button>

                 <button
                  class="btn btn-outline-danger"
                  @click="eliminarEgreso(egr)"
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

  <!-- MODAL: REGISTRAR PAGO -->
  <div
    v-if="modalPagoVisible"
    class="modal-backdrop-custom"
    @click.self="cerrarPago"
  >
    <section class="modal-card" style="max-width: 800px;">
      <div class="panel-header">
        <h3>Registrar Comprobante de Egreso</h3>
        <button class="btn-close" @click="cerrarPago"></button>
      </div>

      <div class="mb-3">
        <h5>Proveedor: <span class="text-primary">{{ proveedorSeleccionado?.nombre }}</span></h5>
        <div class="alert alert-secondary py-2 mb-2">
          <strong>Saldo Total Pendiente:</strong> $ {{ formatDecimal(proveedorSeleccionado?.saldoTotal) }}
        </div>
      </div>

      <form @submit.prevent="guardarPago">
        <div class="row mb-3">
          <div class="col-md-6">
            <label class="form-label">Número de Comprobante (Opcional)</label>
            <input
              v-model="formularioPago.numero"
              class="form-control"
              placeholder="Auto-generado"
            >
          </div>
          <div class="col-md-6">
            <label class="form-label">Observación / Concepto</label>
            <input
              v-model="formularioPago.observacion"
              class="form-control"
              placeholder="p.ej. Cancelación saldo de facturas de compra"
            >
          </div>
        </div>

        <h5 class="mt-4 mb-3">Compras Pendientes</h5>
        <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
          <table class="table table-sm align-middle">
            <thead>
              <tr>
                <th>Factura Compra</th>
                <th>Fecha</th>
                <th>Vencimiento</th>
                <th class="text-end">Total</th>
                <th class="text-end">Saldo</th>
                <th class="text-end" style="width: 150px;">Abonar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="compra in comprasProveedor" :key="compra.id_compra">
                <td>{{ compra.factura || ('Compra #' + compra.id_compra) }}</td>
                <td>{{ formatFechaSimple(compra.fecha) }}</td>
                <td>
                  <span :class="{'text-danger': esVencido(compra.fecha_vencimiento)}">
                    {{ formatFechaSimple(compra.fecha_vencimiento) }}
                  </span>
                </td>
                <td class="text-end">$ {{ formatDecimal(compra.total) }}</td>
                <td class="text-end text-danger fw-bold">$ {{ formatDecimal(compra.saldo) }}</td>
                <td>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text">$</span>
                    <input
                      v-model.number="compra.montoPagar"
                      type="number"
                      class="form-control text-end"
                      :max="compra.saldo"
                      min="0"
                      step="0.01"
                      @input="calcularTotalPago"
                    >
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
          <h4>Total a Pagar: <span class="text-danger">$ {{ formatDecimal(formularioPago.total) }}</span></h4>
          <div class="d-flex gap-2">
            <button
              class="btn btn-secondary"
              type="button"
              @click="cerrarPago"
            >
              Cancelar
            </button>
            <button
              class="btn btn-success"
              type="submit"
              :disabled="guardando || formularioPago.total <= 0"
            >
              {{ guardando ? 'Registrando...' : 'Registrar Pago' }}
            </button>
          </div>
        </div>
      </form>
    </section>
  </div>

  <!-- MODAL: VER DETALLE EGRESO -->
  <div
    v-if="modalDetalleVisible"
    class="modal-backdrop-custom"
    @click.self="cerrarDetalle"
  >
    <section class="modal-card" style="max-width: 600px;">
      <div class="panel-header">
        <h3>Detalle Comprobante de Egreso</h3>
        <button class="btn-close" @click="cerrarDetalle"></button>
      </div>

      <div class="row mb-3" v-if="egresoSeleccionado">
        <div class="col-6 mb-2">
          <strong>Número:</strong><br>{{ egresoSeleccionado.numero }}
        </div>
        <div class="col-6 mb-2">
          <strong>Fecha:</strong><br>{{ formatFechaHora(egresoSeleccionado.fecha) }}
        </div>
        <div class="col-6 mb-2">
          <strong>Proveedor:</strong><br>{{ egresoSeleccionado.proveedor_nombre }}
        </div>
        <div class="col-6 mb-2">
          <strong>Registrado por:</strong><br>{{ egresoSeleccionado.usuario_nombre || 'Sistemas' }}
        </div>
        <div class="col-12 mb-2">
          <strong>Concepto:</strong><br>{{ egresoSeleccionado.observacion || '—' }}
        </div>
      </div>

      <h5 class="mt-4">Facturas Compradas / Pagadas</h5>
      <ul class="list-group mb-3" v-if="egresoSeleccionado">
        <li
          v-for="det in egresoSeleccionado.detalles"
          :key="det.id_detalle"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          <div>
            <strong>Factura Compra:</strong> {{ det.factura_compra || ('Compra #' + det.id_compra) }}
          </div>
          <span class="badge bg-danger fs-6">
            $ {{ formatDecimal(det.valor) }}
          </span>
        </li>
      </ul>

      <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top" v-if="egresoSeleccionado">
        <h4>Total Pagado:</h4>
        <h3 class="text-danger">$ {{ formatDecimal(egresoSeleccionado.total) }}</h3>
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
const cargandoEgresos = ref(false)
const guardando = ref(false)
const error = ref('')

const proveedoresConSaldo = ref([])
const egresos = ref([])

// Modals
const modalPagoVisible = ref(false)
const modalDetalleVisible = ref(false)
const proveedorSeleccionado = ref(null)
const comprasProveedor = ref([])
const egresoSeleccionado = ref(null)

const formularioPago = reactive({
  numero: '',
  observacion: '',
  total: 0
})

const proveedoresFiltrados = computed(() => {
  const query = busqueda.value.toLowerCase()
  if (!query) return proveedoresConSaldo.value

  return proveedoresConSaldo.value.filter(p => 
    p.nombre.toLowerCase().includes(query) || 
    (p.nit && p.nit.includes(query))
  )
})

async function cargarDatos() {
  cargando.value = true
  error.value = ''
  try {
    // Cargar todas las compras
    const responseCompras = await api.get('/compras')
    const compras = responseCompras.data

    // Agrupar compras con saldo > 0 por proveedor
    const agrupado = {}
    compras.forEach(c => {
      const saldo = parseFloat(c.saldo || 0)
      if (saldo > 0) {
        const provNom = c.proveedor || 'Proveedor desconocido'
        const provId = c.id_proveedor
        
        if (!agrupado[provId]) {
          agrupado[provId] = {
            id_proveedor: provId,
            nombre: provNom,
            nit: '', // se rellenará
            saldoTotal: 0,
            comprasCount: 0,
            proximoVencimiento: null,
            comprasLink: []
          }
        }
        
        agrupado[provId].saldoTotal += saldo
        agrupado[provId].comprasCount++
        agrupado[provId].comprasLink.push({
          ...c,
          montoPagar: 0
        })

        if (c.fecha_vencimiento) {
          const fVenc = new Date(c.fecha_vencimiento)
          if (!agrupado[provId].proximoVencimiento || fVenc < new Date(agrupado[provId].proximoVencimiento)) {
            agrupado[provId].proximoVencimiento = c.fecha_vencimiento
          }
        }
      }
    })

    // Cargar lista de proveedores para completar datos del nit
    const responseProveedores = await api.get('/proveedor')
    const proveedoresList = responseProveedores.data

    Object.keys(agrupado).forEach(id => {
      const idNum = parseInt(id)
      const found = proveedoresList.find(p => p.id_proveedor === idNum)
      if (found) {
        agrupado[id].nit = found.nit
      }
    })

    proveedoresConSaldo.value = Object.values(agrupado)
    
    // Cargar egresos
    await cargarEgresos()
  } catch (err) {
    error.value = 'Error al cargar saldos de cartera proveedores.'
    console.error(err)
  } finally {
    cargando.value = false
  }
}

async function cargarEgresos() {
  cargandoEgresos.value = true
  try {
    const res = await api.get('/comprobantes-egreso')
    egresos.value = res.data
  } catch (err) {
    console.error('Error al cargar comprobantes de egreso:', err)
  } finally {
    cargandoEgresos.value = false
  }
}

function abrirPago(prov) {
  proveedorSeleccionado.value = prov
  comprasProveedor.value = prov.comprasLink.map(c => ({ ...c, montoPagar: 0 }))
  formularioPago.numero = ''
  formularioPago.observacion = ''
  formularioPago.total = 0
  modalPagoVisible.value = true
}

function cerrarPago() {
  modalPagoVisible.value = false
  proveedorSeleccionado.value = null
  comprasProveedor.value = []
}

function calcularTotalPago() {
  let sum = 0
  comprasProveedor.value.forEach(c => {
    const val = parseFloat(c.montoPagar || 0)
    sum += val
  })
  formularioPago.total = sum
}

async function guardarPago() {
  if (formularioPago.total <= 0) return
  guardando.value = true
  try {
    const payload = {
      numero: formularioPago.numero || null,
      id_proveedor: proveedorSeleccionado.value.id_proveedor,
      observacion: formularioPago.observacion || null,
      detalles: comprasProveedor.value
        .filter(c => parseFloat(c.montoPagar || 0) > 0)
        .map(c => ({
          id_compra: c.id_compra,
          valor: parseFloat(c.montoPagar)
        }))
    }
    console.log("Payload:", JSON.stringify(payload, null, 2))

    await api.post('/comprobantes-egreso', payload)
    cerrarPago()
    await cargarDatos()
  }catch (err) {

  console.log(err.response.status)
  console.log(err.response.data)

  alert(JSON.stringify(err.response.data, null, 2))

} finally {
    guardando.value = false
  }
}

async function abrirDetalle(idEgreso) {
  try {
    const res = await api.get(`/comprobantes-egreso/${idEgreso}`)
    egresoSeleccionado.value = res.data
    modalDetalleVisible.value = true
  } catch (err) {
    alert('No fue posible cargar el detalle del egreso.')
  }
}

function cerrarDetalle() {
  modalDetalleVisible.value = false
  egresoSeleccionado.value = null
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

async function eliminarEgreso(egreso) {

  const confirmar = confirm(
    `¿Desea eliminar el comprobante de egreso ${egreso.numero}?\n\nEsta acción restaurará los saldos de las compras.`
  )

  if (!confirmar) return

  try {

    await api.delete(`/comprobantes-egreso/${egreso.id_egreso}`)

    await cargarDatos()

    alert("Comprobante de egreso eliminado correctamente.")

  } catch (err) {

    alert(
      err.response?.data?.detail ??
      "No fue posible eliminar el comprobante."
    )

  }

}
</script>
