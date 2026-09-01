<template>

  <div class="container-fluid">

    <div class="card mb-3">

      <div class="card-header">
        <h4 class="mb-0">{{ idCompra ? 'Editar compra' : 'Crear nueva compra' }}</h4>
      </div>

      <div class="card-body">

        <div class="row">

          <div class="col-md-6 mb-3">

            <label class="form-label">Proveedor</label>

            <select
              class="form-select"
              v-model="compra.id_proveedor"
            >
              <option :value="null">Seleccione...</option>

              <option
                v-for="proveedor in proveedores"
                :key="proveedor.id_proveedor"
                :value="proveedor.id_proveedor"
              >
                {{ proveedor.nombre }}
              </option>

            </select>

          </div>

          <div class="col-md-3 mb-3">

            <label class="form-label">Factura</label>

            <input
              class="form-control"
              v-model="compra.factura"
            >

          </div>

          <div class="col-md-3 mb-3">

            <label class="form-label">Medio Pago</label>

            <select
              class="form-select"
              v-model="compra.id_medio_pago"
            >

              <option :value="null">
                Seleccione...
              </option>

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
            v-if="compra.id_medio_pago === 5"
            class="col-md-3 mb-3"
          >

            <label class="form-label">Fecha Vencimiento *</label>

            <input
              v-model="compra.fecha_vencimiento"
              class="form-control"
              type="date"
              required
            >

          </div>

          <div class="col-md-12">

            <label class="form-label">Observación</label>

            <textarea
              rows="2"
              class="form-control"
              v-model="compra.observacion"
            ></textarea>

          </div>

        </div>

      </div>

    </div>

    <ProductoSelector
      @productoSeleccionado="agregarProducto"
    />

    <TablaDetalle
      :detalle="compra.detalle"
      @update:detalle="compra.detalle = $event"
    />

    <div class="card mt-3">

      <div class="card-body">

        <div class="row">

          <div class="col-md-8"></div>

          <div class="col-md-4">

            <table class="table table-sm">

              <tr>

                <th>Subtotal</th>

                <td class="text-end">
                  {{ formato(subtotal) }}
                </td>

              </tr>

              <tr>

                <th>IVA</th>

                <td class="text-end">
                  {{ formato(iva) }}
                </td>

              </tr>

              <tr>

                <th>Total</th>

                <td class="text-end fw-bold">
                  {{ formato(total) }}
                </td>

              </tr>

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
        @click="guardarCompra"
      >
        {{ idCompra ? 'Actualizar Compra' : 'Guardar Compra' }}
      </button>

    </div>

  </div>
</template>

<script setup>

import { ref, reactive, computed, onMounted } from 'vue'

import api from '../services/api.js'

import ProductoSelector from '../components/ProductoSelector.vue'
import TablaDetalle from '../components/TablaDetalle.vue'

const proveedores = ref([])
const mediosPago = ref([])
const props = defineProps({
  idCompra: {
    type: Number,
    default: null,
  },
})
const emit = defineEmits(['consulta'])

const compra = reactive({

    id_proveedor:null,

    factura:'',

    id_medio_pago:null,

    fecha_vencimiento:null,

    observacion:'',

    detalle:[]

})

function agregarProducto(producto){

    compra.detalle.push({

        id_producto: producto.id_producto,

        codigo: producto.codigo,

        nombre: producto.nombre,

        cantidad: 1,

        costo_unitario: 0,

        porcentaje_iva: 19,

        base: 0,

        iva: 0,

        total: 0

    })

}

const subtotal = computed(()=>{

    return compra.detalle.reduce(

        (t,i)=>t+Number(i.base),

        0

    )

})

const iva = computed(()=>{

    return compra.detalle.reduce(

        (t,i)=>t+Number(i.iva),

        0

    )

})

const total = computed(()=>{

    return compra.detalle.reduce(

        (t,i)=>t+Number(i.total),

        0

    )

})

function formato(valor){

    return new Intl.NumberFormat(

        'es-CO',

        {

            style:'currency',

            currency:'COP',

            maximumFractionDigits:0

        }

    ).format(valor)

}

async function cargarProveedores(){

    const response = await api.get('/proveedor')

    proveedores.value = response.data

}

async function cargarMediosPago(){

    const response = await api.get('/medios-pago')

    mediosPago.value = response.data

}

async function guardarCompra() {

  if (!compra.id_proveedor) {

  alert("Seleccione un proveedor.")

  return

}

if (!compra.id_medio_pago) {

  alert("Seleccione un medio de pago.")

  return

}

if (compra.id_medio_pago === 5 && !compra.fecha_vencimiento) {

  alert("Debe especificar una fecha de vencimiento para compras a crédito.")

  return

}

if (compra.detalle.length === 0) {

  alert("Debe agregar al menos un producto.")

  return

}

  try {

    if (props.idCompra) {
      await api.put(`/compras/${props.idCompra}`, compra)
    } else {
      await api.post("/compras", compra)
    }

    alert(props.idCompra ? "Compra actualizada correctamente." : "Compra registrada correctamente.")

    if (props.idCompra) {
      emit('consulta')
    } else {
      limpiarFormulario()
    }

  } catch (err) {

    alert(
      err.response?.data?.detail ??
      "Error al registrar la compra."
    )

  }

}

async function cargarCompra() {
  if (!props.idCompra) return

  const response = await api.get(`/compras/${props.idCompra}`)
  const datos = response.data
  compra.id_proveedor = datos.id_proveedor
  compra.factura = datos.factura ?? ''
  compra.id_medio_pago = datos.id_medio_pago
  compra.fecha_vencimiento = datos.fecha_vencimiento ? datos.fecha_vencimiento.substring(0, 10) : null
  compra.observacion = datos.observacion ?? ''
  compra.detalle = datos.detalle.map((item) => ({
    ...item,
    porcentaje_iva: Number(item.base) > 0
      ? (Number(item.iva) / Number(item.base)) * 100
      : 0,
  }))
}

function cancelar() {
  if (props.idCompra) {
    emit('consulta')
  } else {
    limpiarFormulario()
  }
}

function limpiarFormulario() {

  compra.id_proveedor = null

  compra.factura = ""

  compra.id_medio_pago = null

  compra.fecha_vencimiento = null

  compra.observacion = ""

  compra.detalle = []

}

onMounted(()=>{

    cargarProveedores()

    cargarMediosPago()
    cargarCompra()

})

</script>
