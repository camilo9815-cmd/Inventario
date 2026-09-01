<template>
  <div class="container-fluid py-4">

    <!-- ========================================= -->
    <!-- ENCABEZADO -->
    <!-- ========================================= -->

    <div class="d-flex justify-content-between align-items-center mb-4">

      <div>

        <h2 class="fw-bold mb-1">
          📈 Punto de Equilibrio
        </h2>

        <p class="text-muted mb-0">
          Analiza si las ventas del período cubren todos los gastos del negocio.
        </p>

      </div>

      <div class="d-flex gap-2">

        <select
          class="form-select"
          style="width:170px"
          v-model="mes"
          @change="cargarDatos"
        >

          <option
            v-for="m in meses"
            :key="m.valor"
            :value="m.valor"
          >
            {{ m.nombre }}
          </option>

        </select>

        <input
          class="form-control"
          type="number"
          style="width:120px"
          v-model="anio"
          @change="cargarDatos"
        >

      </div>

    </div>

    <!-- ========================================= -->
    <!-- MENSAJE -->
    <!-- ========================================= -->

    <div
      class="alert"
      :class="'alert-' + datos.salud.color"
    >

      <h5 class="mb-1">

        {{ datos.salud.estado }}

      </h5>

      <small>

        {{ datos.mensaje }}

      </small>

    </div>

    <!-- ========================================= -->
    <!-- ESTADO DE RESULTADOS -->
    <!-- ========================================= -->

    <div class="row g-3 mb-4">

      <div class="col-lg-4">

        <div class="card shadow-sm h-100">

          <div class="card-body">

            <small class="text-muted">

              Ventas

            </small>

            <h3 class="text-success fw-bold">

              $

              {{ formatMoney(datos.estado_resultados.ventas) }}

            </h3>

          </div>

        </div>

      </div>

      <div class="col-lg-4">

        <div class="card shadow-sm h-100">

          <div class="card-body">

            <small class="text-muted">

              Costo de Ventas

            </small>

            <h3 class="text-danger fw-bold">

              $

              {{ formatMoney(datos.estado_resultados.costo_ventas) }}

            </h3>

          </div>

        </div>

      </div>

      <div class="col-lg-4">

        <div class="card shadow-sm h-100">

          <div class="card-body">

            <small class="text-muted">

              Utilidad Bruta

            </small>

            <h3 class="text-primary fw-bold">

              $

              {{ formatMoney(datos.estado_resultados.utilidad_bruta) }}

            </h3>

          </div>

        </div>

      </div>

      <div class="col-lg-4">

        <div class="card shadow-sm h-100">

          <div class="card-body">

            <small class="text-muted">

              Gastos

            </small>

            <h3 class="text-warning fw-bold">

              $

              {{ formatMoney(datos.estado_resultados.gastos) }}

            </h3>

          </div>

        </div>

      </div>

      <div class="col-lg-4">

        <div class="card shadow-sm h-100">

          <div class="card-body">

            <small class="text-muted">

              Utilidad Neta

            </small>

            <h3
              class="fw-bold"
              :class="
                datos.estado_resultados.utilidad_neta >= 0
                  ? 'text-success'
                  : 'text-danger'
              "
            >

              $

              {{ formatMoney(datos.estado_resultados.utilidad_neta) }}

            </h3>

          </div>

        </div>

      </div>

      <div class="col-lg-4">

        <div class="card shadow-sm h-100">

          <div class="card-body">

            <small class="text-muted">

              Margen Bruto

            </small>

            <h3 class="text-info fw-bold">

              {{ datos.estado_resultados.margen_bruto }} %

            </h3>

          </div>

        </div>

      </div>

    </div>

    <!-- ========================================= -->
    <!-- PUNTO DE EQUILIBRIO -->
    <!-- ========================================= -->

    <div class="card shadow-sm mb-4">

      <div class="card-header">

        <strong>

          🎯 Punto de Equilibrio

        </strong>

      </div>

      <div class="card-body">

        <div class="row">

          <div class="col-md-4">

            <h6 class="text-muted">

              Meta de Ventas

            </h6>

            <h3 class="fw-bold text-primary">

              $

              {{ formatMoney(datos.punto_equilibrio.meta) }}

            </h3>

          </div>

          <div class="col-md-4">

            <h6 class="text-muted">

              Ventas Actuales

            </h6>

            <h3 class="fw-bold text-success">

              $

              {{ formatMoney(datos.estado_resultados.ventas) }}

            </h3>

          </div>

          <div class="col-md-4">

            <h6 class="text-muted">

              Avance

            </h6>

            <h3 class="fw-bold">

              {{ datos.punto_equilibrio.avance }} %

            </h3>

          </div>

        </div>

        <div class="progress mt-4" style="height:35px">

          <div
            class="progress-bar progress-bar-striped progress-bar-animated"
            role="progressbar"
            :style="{

                width:

                Math.min(
                    datos.punto_equilibrio.avance,
                    100
                ) + '%'

            }"
          >

            {{ datos.punto_equilibrio.avance }} %

          </div>

        </div>

        <div class="mt-4">

          <h5>

            Faltan

            <span class="text-danger">

              $

              {{ formatMoney(datos.punto_equilibrio.faltante) }}

            </span>

          </h5>

        </div>

      </div>

    </div>

    <!-- ========================================= -->
    <!-- PROYECCIÓN -->
    <!-- ========================================= -->

    <div class="row g-3">

      <div class="col-lg-6">

        <div class="card shadow-sm h-100">

          <div class="card-header">

            Ventas Diarias Necesarias

          </div>

          <div class="card-body">

            <h2 class="fw-bold text-primary">

              $

              {{ formatMoney(datos.punto_equilibrio.ventas_diarias) }}

            </h2>

            <small class="text-muted">

              Valor promedio que debes vender diariamente para alcanzar la meta.

            </small>

          </div>

        </div>

      </div>

      <div class="col-lg-6">

        <div class="card shadow-sm h-100">

          <div class="card-header">

            Proyección de Cierre

          </div>

          <div class="card-body">

            <h2 class="fw-bold text-success">

              $

              {{ formatMoney(datos.punto_equilibrio.proyeccion) }}

            </h2>

            <small class="text-muted">

              Proyección del cierre del mes según el ritmo actual de ventas.

            </small>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'

// ======================================================
// FECHA ACTUAL
// ======================================================

const hoy = new Date()

const mes = ref(hoy.getMonth() + 1)

const anio = ref(hoy.getFullYear())

// ======================================================
// LISTA DE MESES
// ======================================================

const meses = [

    { valor:1,nombre:'Enero' },

    { valor:2,nombre:'Febrero' },

    { valor:3,nombre:'Marzo' },

    { valor:4,nombre:'Abril' },

    { valor:5,nombre:'Mayo' },

    { valor:6,nombre:'Junio' },

    { valor:7,nombre:'Julio' },

    { valor:8,nombre:'Agosto' },

    { valor:9,nombre:'Septiembre' },

    { valor:10,nombre:'Octubre' },

    { valor:11,nombre:'Noviembre' },

    { valor:12,nombre:'Diciembre' }

]

// ======================================================
// ESTADO
// ======================================================

const cargando = ref(false)

const datos = reactive({

    periodo:{

        mes:mes.value,

        anio:anio.value

    },

    estado_resultados:{

        ventas:0,

        costo_ventas:0,

        utilidad_bruta:0,

        gastos:0,

        utilidad_neta:0,

        margen_bruto:0

    },

    punto_equilibrio:{

        meta:0,

        avance:0,

        faltante:0,

        ventas_diarias:0,

        proyeccion:0,

        cumplido:false

    },

    salud:{

        estado:'',

        color:'secondary'

    },

    mensaje:''

})

// ======================================================
// CARGAR DATOS
// ======================================================

async function cargarDatos(){

    cargando.value=true

    try{

        const response=await api.get(
            '/punto-equilibrio',
            {
                params:{
                    mes:mes.value,
                    anio:anio.value
                }
            }
        )

        Object.assign(
            datos,
            response.data
        )

    }

    catch(error){

        console.error(error)

        alert(
            error.response?.data?.detail ??
            'No fue posible cargar el Punto de Equilibrio.'
        )

    }

    finally{

        cargando.value=false

    }

}

// ======================================================
// FORMATO MONEDA
// ======================================================

function formatMoney(valor){

    return Number(valor || 0).toLocaleString(
        'es-CO',
        {

            minimumFractionDigits:0,

            maximumFractionDigits:0

        }
    )

}

// ======================================================
// COLOR DE LA BARRA
// ======================================================

function colorBarra(){

    if(datos.punto_equilibrio.avance>=100)
        return 'bg-success'

    if(datos.punto_equilibrio.avance>=70)
        return 'bg-warning'

    return 'bg-danger'

}

// ======================================================
// PORCENTAJE BARRA
// ======================================================

function porcentajeBarra(){

    if(datos.punto_equilibrio.avance>100)
        return 100

    return datos.punto_equilibrio.avance

}

// ======================================================
// MENSAJE SUPERIOR
// ======================================================

function tituloEstado(){

    if(datos.punto_equilibrio.cumplido)
        return 'Punto de equilibrio alcanzado'

    return 'Punto de equilibrio pendiente'

}

// ======================================================
// UTILIDAD
// ======================================================

function utilidadPositiva(){

    return datos.estado_resultados.utilidad_neta>=0

}

// ======================================================
// INICIO
// ======================================================

onMounted(()=>{

    cargarDatos()

})
</script>
<style scoped>

/* ==========================================================
   CONTENEDOR
========================================================== */

.container-fluid{
    animation: fadeIn .35s ease-in-out;
}


/* ==========================================================
   TITULOS
========================================================== */

h2{

    color:#1f2937;

    font-weight:700;

}

.card-header{

    background:#f8fafc;

    font-weight:600;

}


/* ==========================================================
   CARDS
========================================================== */

.card{

    border:none;

    border-radius:14px;

    transition:.25s;

    box-shadow:0 4px 12px rgba(0,0,0,.05);

}

.card:hover{

    transform:translateY(-3px);

    box-shadow:0 10px 24px rgba(0,0,0,.12);

}


/* ==========================================================
   VALORES
========================================================== */

.card h2,
.card h3{

    font-weight:700;

}

.text-success{

    color:#16a34a !important;

}

.text-danger{

    color:#dc2626 !important;

}

.text-warning{

    color:#d97706 !important;

}

.text-primary{

    color:#2563eb !important;

}

.text-info{

    color:#0891b2 !important;

}


/* ==========================================================
   ALERTA SUPERIOR
========================================================== */

.alert{

    border-radius:14px;

    border:none;

    box-shadow:0 2px 10px rgba(0,0,0,.05);

}

.alert h5{

    margin-bottom:4px;

    font-weight:700;

}


/* ==========================================================
   PROGRESS
========================================================== */

.progress{

    border-radius:25px;

    background:#e5e7eb;

    overflow:hidden;

}

.progress-bar{

    font-weight:700;

    font-size:15px;

    transition:width .8s ease;

}


/* ==========================================================
   ICONOS
========================================================== */

.bi{

    margin-right:6px;

}


/* ==========================================================
   TARJETAS GRANDES
========================================================== */

.card-body{

    padding:1.4rem;

}


/* ==========================================================
   ESTADO FINANCIERO
========================================================== */

.estado-ok{

    color:#16a34a;

    font-weight:700;

}

.estado-warning{

    color:#d97706;

    font-weight:700;

}

.estado-error{

    color:#dc2626;

    font-weight:700;

}


/* ==========================================================
   TABLAS FUTURAS
========================================================== */

table{

    margin-bottom:0;

}

thead{

    background:#f3f4f6;

}

th{

    font-weight:600;

}

tbody tr:hover{

    background:#f9fafb;

}


/* ==========================================================
   BADGES
========================================================== */

.badge{

    padding:.55rem .8rem;

    border-radius:20px;

}


/* ==========================================================
   RESPONSIVE
========================================================== */

@media(max-width:992px){

    .card{

        margin-bottom:15px;

    }

}

@media(max-width:768px){

    h2{

        font-size:24px;

    }

    .card h2{

        font-size:24px;

    }

    .card h3{

        font-size:22px;

    }

}


/* ==========================================================
   ANIMACIONES
========================================================== */

@keyframes fadeIn{

    from{

        opacity:0;

        transform:translateY(15px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

</style>