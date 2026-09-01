<template>
  <div>
    <div class="content-grid">
      <article class="metric-card">
        <span>Productos activos</span>
        <strong>{{ resumen.totalProductos }}</strong>
        <small>Referencias disponibles para operar</small>
      </article>

      <article class="metric-card">
        <span>Bajo stock</span>
        <strong>{{ resumen.bajoStock }}</strong>
        <small>Productos en o por debajo del minimo</small>
      </article>

      <article class="metric-card">
        <span>Sin stock</span>
        <strong>{{ resumen.sinStock }}</strong>
        <small>Referencias con existencia cero</small>
      </article>

      <article class="metric-card">
        <span>Valor inventario compra</span>
        <strong>{{ formatoMoneda(resumen.valorInventario) }}</strong>
        <small>Stock actual por costo promedio</small>
      </article>

        <article class="metric-card">
        <span>Valor inventario precio sugerido venta</span>
        <strong>{{ formatoMoneda(resumen.valorInventarioVenta) }}</strong>
        <small>Stock actual por venta sugerida</small>
      </article>
    </div>

    <section class="panel">
      <div class="panel-header inventory-header">
        <div>
          <p class="eyebrow">Control de existencias</p>
          <h2>Inventario</h2>
        </div>

        <button
          class="btn btn-outline-secondary"
          type="button"
          @click="cargarProductos"
        >
          Actualizar
        </button>
      </div>

      <div class="inventory-toolbar">
        <div class="form-group inventory-search">
          <label for="busqueda">Buscar</label>
          <input
            id="busqueda"
            v-model="busqueda"
            class="form-control"
            placeholder="Codigo o nombre"
          >
        </div>

        <div class="inventory-filters">
          <button
            v-for="opcion in filtros"
            :key="opcion.valor"
            type="button"
            :class="['btn', filtro === opcion.valor ? 'btn-primary' : 'btn-outline-secondary']"
            @click="filtro = opcion.valor"
          >
            {{ opcion.label }}
          </button>
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
              <th>Codigo</th>
              <th>Producto</th>
              <th>Categoria</th>
              <th class="text-end">Stock</th>
              <th class="text-end">Minimo</th>
              <th class="text-end">Costo promedio</th>
              <th class="text-end">Ultimo costo</th>
              <th class="text-end">Precio sugerido</th>
              <th>Estado</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="cargando">
              <td colspan="9">Cargando inventario...</td>
            </tr>

            <tr v-else-if="productosFiltrados.length === 0">
              <td colspan="9">No hay productos para el filtro seleccionado.</td>
            </tr>

            <tr
              v-for="producto in productosFiltrados"
              v-else
              :key="producto.id_producto"
            >
              <td>{{ producto.codigo }}</td>
              <td>
                <strong>{{ producto.nombre }}</strong>
              </td>
              <td>{{ producto.id_categoria }}</td>
              <td class="text-end fw-bold">{{ formatoNumero(producto.stock_actual) }}</td>
              <td class="text-end">{{ formatoNumero(producto.stock_minimo) }}</td>
              <td class="text-end">{{ formatoMoneda(producto.costo_promedio) }}</td>
              <td class="text-end">{{ formatoMoneda(producto.ultimo_costo) }}</td>
              <td class="text-end">{{ formatoMoneda(producto.precio_venta_sugerido) }}</td>
              <td>
                <span :class="['status-pill', estadoProducto(producto).clase]">
                  {{ estadoProducto(producto).texto }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../services/api.js'

const productos = ref([])
const cargando = ref(false)
const error = ref('')
const busqueda = ref('')
const filtro = ref('todos')

const filtros = [
  { valor: 'todos', label: 'Todos' },
  { valor: 'bajo', label: 'Bajo stock' },
  { valor: 'sin', label: 'Sin stock' },
  { valor: 'ok', label: 'OK' },
]

const productosFiltrados = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()

  return productos.value.filter((producto) => {
    const coincideTexto =
      !texto ||
      String(producto.codigo ?? '').toLowerCase().includes(texto) ||
      String(producto.nombre ?? '').toLowerCase().includes(texto)

    if (!coincideTexto) {
      return false
    }

    const estado = estadoProducto(producto).tipo

    if (filtro.value === 'todos') {
      return true
    }

    return estado === filtro.value
  })
})

const resumen = computed(() => {
  return productos.value.reduce(
    (total, producto) => {
      const estado = estadoProducto(producto).tipo

      total.totalProductos += 1
      total.valorInventario += numero(producto.stock_actual) * numero(producto.costo_promedio)
      total.valorInventarioVenta += numero(producto.stock_actual) * numero(producto.precio_venta_sugerido)

      if (estado === 'bajo') {
        total.bajoStock += 1
      }

      if (estado === 'sin') {
        total.sinStock += 1
      }

      return total
    },
    {
      totalProductos: 0,
      bajoStock: 0,
      sinStock: 0,
      valorInventario: 0,
      valorInventarioVenta: 0,
    }
  )
})

async function cargarProductos() {
  cargando.value = true
  error.value = ''

  try {
    const response = await api.get('/productos')
    productos.value = response.data
  } catch {
    error.value = 'No fue posible cargar el inventario.'
  } finally {
    cargando.value = false
  }
}

function estadoProducto(producto) {
  const stock = numero(producto.stock_actual)
  const minimo = numero(producto.stock_minimo)

  if (stock <= 0) {
    return {
      tipo: 'sin',
      texto: 'Sin stock',
      clase: 'inactive',
    }
  }

  if (stock <= minimo) {
    return {
      tipo: 'bajo',
      texto: 'Bajo',
      clase: 'warning',
    }
  }

  return {
    tipo: 'ok',
    texto: 'OK',
    clase: 'active',
  }
}

function numero(valor) {
  return Number(valor ?? 0)
}

function formatoNumero(valor) {
  return new Intl.NumberFormat('es-CO', {
    maximumFractionDigits: 2,
  }).format(numero(valor))
}

function formatoMoneda(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(numero(valor))
}

onMounted(cargarProductos)
</script>
