<template>
  <section class="panel">

    <div class="panel-header">

      <div>
        <p class="eyebrow">Catálogo</p>
        <h2>Proveedores</h2>
      </div>

      <button
        class="btn btn-primary"
        type="button"
        @click="toggleFormulario"
      >
        {{ mostrarFormulario ? 'Cerrar' : 'Nuevo proveedor' }}
      </button>

    </div>

    <form
      v-if="mostrarFormulario"
      class="product-form"
      @submit.prevent="guardarProveedor"
    >

      <div class="form-group">
        <label>NIT</label>

        <input
          v-model="form.nit"
          class="form-control"
          required
        >
      </div>

      <div class="form-group wide">
        <label>Nombre</label>

        <input
          v-model="form.nombre"
          class="form-control"
          required
        >
      </div>

      <div class="form-group">
        <label>Teléfono</label>

        <input
          v-model="form.telefono"
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label>Correo</label>

        <input
          v-model="form.correo"
          class="form-control"
          type="email"
        >
      </div>

      <div class="form-group wide">
        <label>Dirección</label>

        <input
          v-model="form.direccion"
          class="form-control"
        >
      </div>

      <div class="form-actions">

        <button
          class="btn btn-success"
          type="submit"
          :disabled="guardando"
        >

          {{ form.id_proveedor ? 'Actualizar' : 'Guardar' }}

        </button>

      </div>

    </form>

    <div
      v-if="mensaje"
      class="alert alert-success"
    >

      {{ mensaje }}

    </div>

    <div
      v-if="error"
      class="alert alert-danger"
    >

      {{ error }}

    </div>

    <div class="table-responsive">

      <table class="table align-middle">

        <thead>

        <tr>

          <th>NIT</th>

          <th>Nombre</th>

          <th>Teléfono</th>

          <th>Correo</th>

          <th>Dirección</th>

          <th>Estado</th>

          <th>Acciones</th>

        </tr>

        </thead>

        <tbody>

        <tr v-if="cargando">

          <td colspan="7">

            Cargando proveedores...

          </td>

        </tr>

        <tr
          v-else-if="proveedores.length==0"
        >

          <td colspan="7">

            No existen proveedores registrados.

          </td>

        </tr>

        <tr
          v-for="proveedor in proveedores"
          :key="proveedor.id_proveedor"
        >

          <td>{{ proveedor.nit }}</td>

          <td>{{ proveedor.nombre }}</td>

          <td>{{ proveedor.telefono }}</td>

          <td>{{ proveedor.correo }}</td>

          <td>{{ proveedor.direccion }}</td>

          <td>

            <span
              :class="[
                'status-pill',
                proveedor.activo ? 'active':'inactive'
              ]"
            >

              {{ proveedor.activo ? 'Activo':'Inactivo' }}

            </span>

          </td>

          <td>

            <button
              class="btn btn-warning btn-sm me-2"
              @click="seleccionarProveedor(proveedor)"
            >

              Editar

            </button>

            <button
              class="btn btn-danger btn-sm"
              @click="eliminarProveedor(proveedor.id_proveedor)"
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

const proveedores = ref([])
const cargando = ref(false)
const guardando = ref(false)
const mostrarFormulario = ref(false)

const mensaje = ref('')
const error = ref('')

const form = reactive({
  id_proveedor: null,
  nit: '',
  nombre: '',
  telefono: '',
  correo: '',
  direccion: ''
})

function resetForm() {

  form.id_proveedor = null
  form.nit = ''
  form.nombre = ''
  form.telefono = ''
  form.correo = ''
  form.direccion = ''

}

async function cargarProveedores() {

  cargando.value = true
  error.value = ''

  try {

    const response = await api.get('/proveedor')

    proveedores.value = response.data

  } catch {

    error.value = 'No fue posible cargar los proveedores.'

  } finally {

    cargando.value = false

  }

}

async function guardarProveedor() {

  guardando.value = true
  mensaje.value = ''
  error.value = ''

  try {

    if (form.id_proveedor) {

      await api.put(
        `/proveedor/${form.id_proveedor}`,
        { ...form }
      )

      mensaje.value = 'Proveedor actualizado correctamente.'

    } else {

      await api.post(
        '/proveedor',
        { ...form }
      )

      mensaje.value = 'Proveedor creado correctamente.'

    }

    resetForm()

    mostrarFormulario.value = false

    await cargarProveedores()

  } catch (err) {

    error.value =
      err.response?.data?.detail ??
      'No fue posible guardar el proveedor.'

  } finally {

    guardando.value = false

  }

}

async function eliminarProveedor(id) {

  if (!confirm("¿Desea eliminar este proveedor?")) {
    return
  }

  try {

    await api.delete(`/proveedor/${id}`)

    mensaje.value = 'Proveedor eliminado correctamente.'

    await cargarProveedores()

  } catch (err) {

    error.value =
      err.response?.data?.detail ??
      'No fue posible eliminar el proveedor.'

  }

}

function seleccionarProveedor(proveedor) {

  form.id_proveedor = proveedor.id_proveedor

  form.nit = proveedor.nit

  form.nombre = proveedor.nombre

  form.telefono = proveedor.telefono

  form.correo = proveedor.correo

  form.direccion = proveedor.direccion

  mostrarFormulario.value = true

}

function toggleFormulario() {

  resetForm()

  mensaje.value = ''
  error.value = ''

  mostrarFormulario.value = !mostrarFormulario.value

}

onMounted(() => {

  cargarProveedores()

})
</script>