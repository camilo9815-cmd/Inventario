<template>
    <div class="panel-header">



</div>

  <section class="panel">
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

            <th>Proveedor</th>

            <th>Medio Pago</th>

            <th>Total</th>

            <th>Acciones</th>

          </tr>

        </thead>

        <tbody>

          <tr v-if="cargando">

            <td colspan="7">
              Cargando compras...
            </td>

          </tr>

          <tr
            v-else-if="compras.length==0"
          >

            <td colspan="7">
              No existen compras registradas.
            </td>

          </tr>

          <tr
            v-for="compra in compras"
            :key="compra.id_compra"
          >

            <td>{{ compra.id_compra }}</td>

            <td>{{ formatearFecha(compra.fecha) }}</td>

            <td>{{ compra.factura }}</td>

            <td>{{ compra.proveedor }}</td>

            <td>{{ compra.medio_pago }}</td>

            <td>{{ formatoMoneda(compra.total) }}</td>

            <td>

              <button
                class="btn btn-primary btn-sm me-2"
                @click="verCompra(compra.id_compra)"
              >
                Ver
              </button>

              <button
                class="btn btn-outline-primary btn-sm me-2"
                type="button"
                @click="emit('editar', compra.id_compra)"
              >
                Editar
              </button>

              <button
                class="btn btn-outline-danger btn-sm"
                type="button"
                @click="eliminarCompra(compra)"
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

import { ref, onMounted } from "vue"

import api from "../services/api"


const compras = ref([])

const cargando = ref(false)

const error = ref("")

async function cargarCompras(){

    cargando.value = true

    error.value = ""

    try{

        const response = await api.get("/compras")

        compras.value = response.data

    }catch(err){

        error.value = "No fue posible cargar las compras."

    }finally{

        cargando.value = false

    }

}

const emit = defineEmits([
    "ver",
    "editar"
])

function verCompra(id){

    emit("ver", id)

}

async function eliminarCompra(compra) {
    if (!confirm(`¿Eliminar la compra #${compra.id_compra}? Esta acción ajustará el inventario.`)) {
        return
    }

    try {
        await api.delete(`/compras/${compra.id_compra}`)
        await cargarCompras()
    } catch (err) {
        alert(err.response?.data?.detail ?? "No fue posible eliminar la compra.")
    }
}

function formatoMoneda(valor){

    return new Intl.NumberFormat(

        "es-CO",

        {

            style:"currency",

            currency:"COP",

            maximumFractionDigits:0

        }

    ).format(Number(valor))

}

function formatearFecha(fecha){

    return new Date(fecha).toLocaleDateString("es-CO")

}

onMounted(cargarCompras)

</script>
