<template>
  <section class="content-grid">

  </section>
</template>

<script setup>
const metrics = [
  { label: 'Ingresos del mes', value: '$0', detail: 'Pendiente ventas' },
  { label: 'Productos bajos', value: '0', detail: 'Según stock mínimo' },
  { label: 'IVA neto', value: '$0', detail: 'Ventas - compras - gastos' },
  { label: 'Valor inventario', value: '$0', detail: 'Costo promedio' },
]

const modules = [
  { name: 'Login y seguridad', status: 'Activo' },
  { name: 'Productos', status: 'Activo' },
  { name: 'Proveedores', status: 'Activo' },
  { name: 'Compras', status: 'Activo' },
  { name: 'Ventas', status: 'Activo' },
  { name: 'Inventario automático', status: 'Activo' },
]


import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'

const meses = [
  { valor: 1, nombre: 'Enero' },
  { valor: 2, nombre: 'Febrero' },
  { valor: 3, nombre: 'Marzo' },
  { valor: 4, nombre: 'Abril' },
  { valor: 5, nombre: 'Mayo' },
  { valor: 6, nombre: 'Junio' },
  { valor: 7, nombre: 'Julio' },
  { valor: 8, nombre: 'Agosto' },
  { valor: 9, nombre: 'Septiembre' },
  { valor: 10, nombre: 'Octubre' },
  { valor: 11, nombre: 'Noviembre' },
  { valor: 12, nombre: 'Diciembre' }
]

const hoy = new Date()

const periodo = reactive({
  mes: hoy.getMonth() + 1,
  anio: hoy.getFullYear()
})

const dashboard = reactive({

  ventas: {
    total: 0,
    cantidad: 0
  },

  compras: {
    total: 0,
    cantidad: 0
  },

  gastos: {
    total: 0
  },

  utilidad: {
    total: 0
  },

  tesoreria: {

    por_cobrar: 0,

    por_pagar: 0,

    flujo: 0

  },

  inventario: {

    total: 0

  },

  top_clientes: [],

  top_proveedores: [],

  stock_bajo: [],

  alertas: []

})

function formatMoney(valor){

    return Number(valor || 0)
        .toLocaleString(
            'es-CO',
            {
                minimumFractionDigits:0
            }
        )

}

async function cargarDashboard(){

    try{

        const response = await api.get(
            '/dashboard',
            {
                params:{
                    mes:periodo.mes,
                    anio:periodo.anio
                }
            }
        )

        Object.assign(
            dashboard,
            response.data
        )

    }

    catch(error){

        console.log(error)

    }

}

onMounted(()=>{

    // Lo activaremos cuando exista el endpoint

    // cargarDashboard()

})

</script>