<template>
  <div>
    <section class="panel expense-period">
      <div class="panel-header">
        <div>
          <p class="eyebrow">Control mensual</p>
          <h2>Gastos y cobertura</h2>
        </div>

        <div class="period-controls">
          <select
            v-model.number="periodo.mes"
            class="form-select"
            aria-label="Mes"
            @change="cargarTodo"
          >
            <option
              v-for="(nombre, index) in meses"
              :key="nombre"
              :value="index + 1"
            >
              {{ nombre }}
            </option>
          </select>

          <input
            v-model.number="periodo.anio"
            class="form-control"
            type="number"
            min="2020"
            max="2100"
            aria-label="Ano"
            @change="cargarTodo"
          >
        </div>
      </div>

      <div class="coverage-layout">
        <div>
          <div class="coverage-heading">
            <span>Cobertura de gastos fijos</span>
            <strong>{{ formatoPorcentaje(resumen.porcentaje_cobertura_fijos) }}</strong>
          </div>

          <div class="coverage-track">
            <div
              class="coverage-value"
              :class="{ complete: resumen.gastos_fijos_cubiertos }"
              :style="{ width: `${porcentajeBarra}%` }"
            ></div>
          </div>
        </div>

        <span :class="['coverage-status', resumen.gastos_fijos_cubiertos ? 'covered' : 'pending']">
          {{ resumen.gastos_fijos_cubiertos ? 'Gastos fijos cubiertos' : 'Cobertura pendiente' }}
        </span>
      </div>
    </section>

    <div class="finance-grid">
      <article class="metric-card">
        <span>Ventas sin IVA</span>
        <strong>{{ formatoMoneda(resumen.ventas_base) }}</strong>
        <small>Total facturado: {{ formatoMoneda(resumen.ventas_total) }}</small>
      </article>

      <article class="metric-card reserve-card">
        <span>Reposicion minima</span>
        <strong>{{ formatoMoneda(resumen.dinero_reposicion) }}</strong>
        <small>Costo de la mercancia vendida</small>
      </article>

      <article class="metric-card purchase-card">
        <span>Disponible para comprar</span>
        <strong>{{ formatoMoneda(resumen.disponible_para_compras) }}</strong>
        <small>Despues de cubrir los gastos del mes</small>
      </article>

      <article class="metric-card">
        <span>Utilidad bruta</span>
        <strong>{{ formatoMoneda(resumen.utilidad_bruta) }}</strong>
        <small>Ventas menos costo de productos</small>
      </article>

      <article class="metric-card">
        <span>Gastos del mes</span>
        <strong>{{ formatoMoneda(resumen.gastos_totales) }}</strong>
        <small>Fijos {{ formatoMoneda(resumen.gastos_fijos) }}</small>
      </article>

      <article :class="['metric-card', resultadoClase]">
        <span>Disponible despues de gastos</span>
        <strong>{{ formatoMoneda(resumen.utilidad_despues_gastos) }}</strong>
        <small>
          {{ resumen.utilidad_despues_gastos >= 0 ? 'Resultado operativo positivo' : 'Los gastos superan el margen' }}
        </small>
      </article>

      <article class="metric-card">
        <span>IVA neto estimado</span>
        <strong>{{ formatoMoneda(resumen.iva_neto) }}</strong>
        <small>IVA ventas menos IVA de gastos</small>
      </article>
    </div>

    <section class="panel">
      <div class="panel-header">
        <div>
          <p class="eyebrow">Egreso</p>
          <h2>Registrar gasto</h2>
        </div>

        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="mostrarFormulario = !mostrarFormulario"
        >
          {{ mostrarFormulario ? 'Cerrar' : 'Nuevo gasto' }}
        </button>
      </div>

      <form
        v-if="mostrarFormulario"
        class="expense-form"
        @submit.prevent="guardarGasto"
      >
        <div class="form-group">
          <label for="fecha-gasto">Fecha</label>
          <input
            id="fecha-gasto"
            v-model="form.fecha"
            class="form-control"
            type="date"
            required
          >
        </div>

        <div class="form-group">
          <label for="tipo-gasto">Tipo</label>
          <select
            id="tipo-gasto"
            v-model="form.id_tipo_gasto"
            class="form-select"
            required
          >
            <option :value="null">Seleccione...</option>
            <option
              v-for="tipo in tipos"
              :key="tipo.id_tipo_gasto"
              :value="tipo.id_tipo_gasto"
            >
              {{ tipo.nombre }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="categoria-gasto">Categoria</label>
          <select
            id="categoria-gasto"
            v-model="form.id_categoria_gasto"
            class="form-select"
            required
          >
            <option :value="null">Seleccione...</option>
            <option
              v-for="categoria in categorias"
              :key="categoria.id_categoria_gasto"
              :value="categoria.id_categoria_gasto"
            >
              {{ categoria.nombre }}
            </option>
          </select>
        </div>

        <div class="form-group wide">
          <label for="concepto-gasto">Concepto</label>
          <input
            id="concepto-gasto"
            v-model.trim="form.concepto"
            class="form-control"
            maxlength="250"
            required
          >
        </div>

        <div class="form-group">
          <label for="base-gasto">Base</label>
          <input
            id="base-gasto"
            v-model.number="form.base"
            class="form-control"
            type="number"
            min="0.01"
            step="0.01"
            required
          >
        </div>

        <div class="form-group">
          <label for="medio-gasto">Medio de pago</label>
          <select
            id="medio-gasto"
            v-model="form.id_medio_pago"
            class="form-select"
            required
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

        <div class="form-group">
          <label class="form-check-label" for="aplica-iva">IVA</label>
          <div class="iva-control">
            <input
              id="aplica-iva"
              v-model="form.aplica_iva"
              class="form-check-input"
              type="checkbox"
            >
            <input
              v-model.number="form.porcentaje_iva"
              class="form-control"
              type="number"
              min="0"
              max="100"
              step="0.01"
              :disabled="!form.aplica_iva"
              aria-label="Porcentaje de IVA"
            >
          </div>
        </div>

        <div class="form-group wide">
          <label for="observacion-gasto">Observacion</label>
          <input
            id="observacion-gasto"
            v-model="form.observacion"
            class="form-control"
            maxlength="250"
          >
        </div>

        <div class="expense-form-total">
          <span>Total</span>
          <strong>{{ formatoMoneda(totalFormulario) }}</strong>
        </div>

        <div class="form-actions">
          <button
            class="btn btn-success"
            type="submit"
            :disabled="guardando"
          >
            Guardar gasto
          </button>
        </div>
      </form>

      <div
        v-if="error"
        class="alert alert-danger"
      >
        {{ error }}
      </div>

      <div class="expense-summary">
        <span>Fijos: <strong>{{ formatoMoneda(resumen.gastos_fijos) }}</strong></span>
        <span>Variables: <strong>{{ formatoMoneda(resumen.gastos_variables) }}</strong></span>
        <span v-if="resumen.faltante_gastos_fijos > 0">
          Faltante fijos: <strong>{{ formatoMoneda(resumen.faltante_gastos_fijos) }}</strong>
        </span>
      </div>

      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Tipo</th>
              <th>Categoria</th>
              <th>Concepto</th>
              <th>Medio pago</th>
              <th class="text-end">Base</th>
              <th class="text-end">IVA</th>
              <th class="text-end">Total</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="cargando">
              <td colspan="8">Cargando gastos...</td>
            </tr>

            <tr v-else-if="gastos.length === 0">
              <td colspan="8">No hay gastos registrados en este periodo.</td>
            </tr>

            <tr
              v-for="gasto in gastos"
              v-else
              :key="gasto.id_gasto"
            >
              <td>{{ formatoFecha(gasto.fecha) }}</td>
              <td>
                <span class="expense-type">{{ gasto.tipo }}</span>
              </td>
              <td>{{ gasto.categoria }}</td>
              <td>{{ gasto.concepto }}</td>
              <td>{{ gasto.medio_pago }}</td>
              <td class="text-end">{{ formatoMoneda(gasto.base) }}</td>
              <td class="text-end">{{ formatoMoneda(gasto.iva) }}</td>
              <td class="text-end fw-bold">{{ formatoMoneda(gasto.total) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '../services/api.js'

const hoy = new Date()
const fechaHoy = [
  hoy.getFullYear(),
  String(hoy.getMonth() + 1).padStart(2, '0'),
  String(hoy.getDate()).padStart(2, '0'),
].join('-')

const meses = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

const periodo = reactive({
  anio: hoy.getFullYear(),
  mes: hoy.getMonth() + 1,
})

const resumen = reactive({
  ventas_base: 0,
  ventas_total: 0,
  dinero_reposicion: 0,
  disponible_para_compras: 0,
  utilidad_bruta: 0,
  gastos_fijos: 0,
  gastos_variables: 0,
  gastos_totales: 0,
  iva_neto: 0,
  utilidad_despues_gastos: 0,
  porcentaje_cobertura_fijos: 0,
  faltante_gastos_fijos: 0,
  gastos_fijos_cubiertos: false,
})

const form = reactive({
  fecha: fechaHoy,
  id_tipo_gasto: null,
  id_categoria_gasto: null,
  concepto: '',
  base: 0,
  aplica_iva: false,
  porcentaje_iva: 19,
  id_medio_pago: null,
  observacion: '',
})

const tipos = ref([])
const categorias = ref([])
const mediosPago = ref([])
const gastos = ref([])
const cargando = ref(false)
const guardando = ref(false)
const mostrarFormulario = ref(false)
const error = ref('')

const porcentajeBarra = computed(() => {
  return Math.min(100, Math.max(0, Number(resumen.porcentaje_cobertura_fijos ?? 0)))
})

const totalFormulario = computed(() => {
  const base = Number(form.base ?? 0)
  const iva = form.aplica_iva
    ? base * (Number(form.porcentaje_iva ?? 0) / 100)
    : 0

  return base + iva
})

const resultadoClase = computed(() => {
  return Number(resumen.utilidad_despues_gastos) >= 0
    ? 'positive-card'
    : 'negative-card'
})

async function cargarCatalogos() {
  const [tiposResponse, categoriasResponse, mediosResponse] = await Promise.all([
    api.get('/tipos-gasto'),
    api.get('/categorias-gasto'),
    api.get('/medios-pago'),
  ])

  tipos.value = tiposResponse.data
  categorias.value = categoriasResponse.data
  mediosPago.value = mediosResponse.data
}

async function cargarTodo() {
  cargando.value = true
  error.value = ''

  try {
    const params = {
      anio: periodo.anio,
      mes: periodo.mes,
    }

    const [gastosResponse, resumenResponse] = await Promise.all([
      api.get('/gastos', { params }),
      api.get('/gastos/resumen-mensual', { params }),
    ])

    gastos.value = gastosResponse.data
    Object.assign(resumen, resumenResponse.data)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'No fue posible cargar los gastos.'
  } finally {
    cargando.value = false
  }
}

async function guardarGasto() {
  guardando.value = true
  error.value = ''

  try {
    await api.post('/gastos', {
      ...form,
      fecha: `${form.fecha}T12:00:00`,
    })

    const fecha = new Date(`${form.fecha}T12:00:00`)
    periodo.anio = fecha.getFullYear()
    periodo.mes = fecha.getMonth() + 1
    limpiarFormulario()
    mostrarFormulario.value = false
    await cargarTodo()
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'No fue posible registrar el gasto.'
  } finally {
    guardando.value = false
  }
}

function limpiarFormulario() {
  form.fecha = fechaHoy
  form.id_tipo_gasto = null
  form.id_categoria_gasto = null
  form.concepto = ''
  form.base = 0
  form.aplica_iva = false
  form.porcentaje_iva = 19
  form.id_medio_pago = null
  form.observacion = ''
}

function formatoMoneda(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(valor ?? 0))
}

function formatoPorcentaje(valor) {
  return `${Number(valor ?? 0).toFixed(1)}%`
}

function formatoFecha(fecha) {
  return new Date(fecha).toLocaleDateString('es-CO')
}

onMounted(async () => {
  try {
    await cargarCatalogos()
    await cargarTodo()
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'No fue posible iniciar el modulo de gastos.'
  }
})
</script>
