<template>
  <div class="card shadow-sm mb-3">

    <div class="card-header">
      <strong>Buscar producto</strong>
    </div>

    <div class="card-body position-relative">

      <input
        ref="inputBusqueda"
        v-model="busqueda"
        class="form-control"
        placeholder="Código o nombre..."
        autocomplete="off"
        @keydown.down.prevent="bajar"
        @keydown.up.prevent="subir"
        @keydown.enter.prevent="seleccionarActual"
        @keydown.esc="cerrarLista"
      >

      <div
        v-if="mostrarLista"
        class="list-group position-absolute w-100 mt-1 shadow"
        style="z-index:1000; max-height:300px; overflow:auto;"
      >

        <button

          v-for="(producto,index) in productosFiltrados"

          :key="producto.id_producto"

          class="list-group-item list-group-item-action"

          :class="{ active:indexSeleccionado===index }"

          @click="seleccionarProducto(producto)"

        >

          <strong>{{ producto.codigo }}</strong>

          -

          {{ producto.nombre }}

        </button>

      </div>

    </div>

  </div>
</template>

<script setup>

import {
    ref,
    computed,
    onMounted,
    nextTick
} from "vue"

import api from "../services/api"

const emit = defineEmits([
    "productoSeleccionado"
])

const productos = ref([])

const busqueda = ref("")

const inputBusqueda = ref(null)

const indexSeleccionado = ref(0)

async function cargarProductos(){

    const response = await api.get("/productos")

    productos.value = response.data

}

const productosFiltrados = computed(()=>{

    const texto = busqueda.value.trim().toLowerCase()

    if(texto.length<2){

        return []

    }

    return productos.value.filter(p=>

        p.codigo.toLowerCase().includes(texto)

        ||

        p.nombre.toLowerCase().includes(texto)

    )

})

const mostrarLista = computed(()=>{

    return productosFiltrados.value.length>0

})

function bajar(){

    if(indexSeleccionado.value<productosFiltrados.value.length-1){

        indexSeleccionado.value++

    }

}

function subir(){

    if(indexSeleccionado.value>0){

        indexSeleccionado.value--

    }

}

function seleccionarActual(){

    if(productosFiltrados.value.length===0){

        return

    }

    seleccionarProducto(

        productosFiltrados.value[indexSeleccionado.value]

    )

}

async function seleccionarProducto(producto){

    emit(

        "productoSeleccionado",

        producto

    )

    busqueda.value=""

    indexSeleccionado.value=0

    await nextTick()

    inputBusqueda.value.focus()

}

function cerrarLista(){

    busqueda.value=""

    indexSeleccionado.value=0

}

onMounted(cargarProductos)



</script>