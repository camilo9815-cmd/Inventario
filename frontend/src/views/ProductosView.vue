<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Catálogo</p>
        <h2>Productos</h2>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="toggleFormulario"
      >
        {{ mostrarFormulario ? 'Cerrar' : 'Nuevo producto' }}
      </button>
    </div>

    <form
      v-if="mostrarFormulario"
      class="product-form"
      @submit.prevent="guardarProducto"
    >
      <div class="form-group">
        <label for="codigo">Código</label>
        <input
          id="codigo"
          v-model="form.codigo"
          class="form-control"
          required
        >
      </div>

      <div class="form-group wide">
        <label for="nombre">Nombre</label>
        <input
          id="nombre"
          v-model="form.nombre"
          class="form-control"
          required
        >
      </div>

      <div class="form-group">
        <label for="categoria">Categoría</label>
        <input
          id="categoria"
          v-model.number="form.id_categoria"
          class="form-control"
          type="number"
          min="1"
          required
        >
      </div>

      <div class="form-group">
        <label for="stock">Stock mínimo</label>
        <input
          id="stock"
          v-model.number="form.stock_minimo"
          class="form-control"
          type="number"
          min="0"
          step="0.01"
          required
        >
      </div>

      <div class="form-group">
        <label for="precio">Precio sugerido</label>
        <input
          id="precio"
          v-model.number="form.precio_venta_sugerido"
          class="form-control"
          type="number"
          min="0"
          step="0.01"
          required
        >
      </div>

      <div class="form-actions">
        <button
          class="btn btn-success"
          type="submit"
          :disabled="guardando"
        >
         {{ form.id_producto ? 'Actualizar' : 'Guardar' }}
        </button>
      </div>
    </form>

    <div
      v-if="mensaje"
      class="alert alert-success"
      role="alert"
    >
      {{ mensaje }}
    </div>

    <div
      v-if="error"
      class="alert alert-danger"
      role="alert"
    >
      {{ error }}
    </div>

    <div class="table-responsive">
      <table class="table align-middle">
        <thead>
          <tr>
            <th>Código</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Stock mínimo</th>
            <th>Precio sugerido</th>
            <th>Estado</th>
            <th>Accion</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="cargando">
            <td colspan="6">Cargando productos...</td>
          </tr>
          <tr v-else-if="productos.length === 0">
            <td colspan="6">No hay productos registrados.</td>
          </tr>
          <tr
            v-for="producto in productos"
            v-else
            :key="producto.id_producto"
          >
            <td>{{ producto.codigo }}</td>
            <td>{{ producto.nombre }}</td>
            <td>{{ producto.id_categoria }}</td>
            <td>{{ producto.stock_minimo }}</td>
            <td>{{ formatCurrency(producto.precio_venta_sugerido) }}</td>
            <td>
              <span :class="['status-pill', producto.activo ? 'active' : 'inactive']">
                {{ producto.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <button
                  class="btn btn-warning btn-sm me-2"
                  @click="seleccionarProducto(producto)"
              >
                  Editar
              </button>
              <button
                  class="btn btn-danger btn-sm"
                  @click="eliminarProducto(producto.id_producto)"
              >
                  X
              </button>
          </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../services/api'

const productos = ref([])
const cargando = ref(false)
const guardando = ref(false)
const mostrarFormulario = ref(false)
const mensaje = ref('')
const error = ref('')

const form = reactive({
  id_producto: null,
  codigo: '',
  nombre: '',
  id_categoria: 1,
  stock_minimo: 0,
  precio_venta_sugerido: 0,
})

function resetForm() {
  form.id_producto = null
  form.codigo = ''
  form.nombre = ''
  form.id_categoria = 1
  form.stock_minimo = 0
  form.precio_venta_sugerido = 0
}

function formatCurrency(value) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(value ?? 0))
}

async function cargarProductos() {
  cargando.value = true
  error.value = ''

  try {
    const response = await api.get('/productos')
    productos.value = response.data
  } catch {
    error.value = 'No fue posible cargar los productos.'
  } finally {
    cargando.value = false
  }
}

async function guardarProducto() {
  guardando.value = true
  mensaje.value = ''
  error.value = ''

  try {

    if (form.id_producto) {

      await api.put(
        `/productos/${form.id_producto}`,
        { ...form }
      )

      mensaje.value = 'Producto actualizado correctamente.'

    } else {

      await api.post(
        '/productos',
        { ...form }
      )

      mensaje.value = 'Producto creado correctamente.'

    }

    resetForm()
    mostrarFormulario.value = false
    await cargarProductos()

  } catch (err) {

    error.value =
      err.response?.data?.detail ??
      'No fue posible guardar el producto.'

  } finally {

    guardando.value = false
  }
}

async function eliminarProducto(id) {

  if (!confirm("¿Desea eliminar este producto?")) {
    return
  }

  try {

    await api.delete(`/productos/${id}`)

    await cargarProductos()

  } catch (err) {

    alert(
      err.response?.data?.detail ??
      "No fue posible eliminar."
    )

  }

}

function seleccionarProducto(producto) {

  form.id_producto = producto.id_producto
  form.codigo = producto.codigo
  form.nombre = producto.nombre
  form.id_categoria = producto.id_categoria
  form.stock_minimo = producto.stock_minimo
  form.precio_venta_sugerido = producto.precio_venta_sugerido

  mostrarFormulario.value = true
}

function editarProducto(producto) {

  form.id_producto = producto.id_producto
  form.codigo = producto.codigo
  form.nombre = producto.nombre
  form.id_categoria = producto.id_categoria
  form.stock_minimo = producto.stock_minimo
  form.precio_venta_sugerido = producto.precio_venta_sugerido

  mostrarFormulario.value = true

}

function toggleFormulario() {
  resetForm()
  mensaje.value = ''
  error.value = ''

  mostrarFormulario.value = !mostrarFormulario.value
}

onMounted(cargarProductos)
</script>
