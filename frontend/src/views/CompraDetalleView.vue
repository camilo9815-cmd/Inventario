<template>

<div
    class="container-fluid"
    v-if="compra"
>

    <div class="card">

        <div class="card-header d-flex justify-content-between align-items-center">

            <h4 class="mb-0">

                Compra #{{ compra.id_compra }}

            </h4>

             <button
            class="btn btn-primary me-2"
            @click="imprimir"
        >
            🖨 Imprimir
        </button>

            <button
                class="btn btn-secondary"
                @click="emit('volver')"
            >
                Volver
            </button>

        </div>

        <div class="card-body">

            <div class="row mb-4">

                <div class="col-md-3">

                    <strong>Proveedor</strong>

                    <div>{{ compra.proveedor }}</div>

                </div>

                <div class="col-md-3">

                    <strong>Factura</strong>

                    <div>{{ compra.factura }}</div>

                </div>

                <div class="col-md-3">

                    <strong>Fecha</strong>

                    <div>{{ formatearFecha(compra.fecha) }}</div>

                </div>

                <div class="col-md-3">

                    <strong>Medio Pago</strong>

                    <div>{{ compra.medio_pago }}</div>

                </div>

            </div>

            <table class="table table-bordered table-hover">

                <thead class="table-light">

                    <tr>

                        <th>Código</th>

                        <th>Producto</th>

                        <th class="text-center">Cantidad</th>

                        <th class="text-end">Costo</th>

                        <th class="text-end">Base</th>

                        <th class="text-end">IVA</th>

                        <th class="text-end">Total</th>

                    </tr>

                </thead>

                <tbody>

                    <tr
                        v-for="item in compra.detalle"
                        :key="item.id_detalle_compra"
                    >

                        <td>{{ item.codigo }}</td>

                        <td>{{ item.nombre }}</td>

                        <td class="text-center">

                            {{ item.cantidad }}

                        </td>

                        <td class="text-end">

                            {{ formato(item.costo_unitario) }}

                        </td>

                        <td class="text-end">

                            {{ formato(item.base) }}

                        </td>

                        <td class="text-end">

                            {{ formato(item.iva) }}

                        </td>

                        <td class="text-end fw-bold">

                            {{ formato(item.total) }}

                        </td>

                    </tr>

                </tbody>

            </table>

            <div class="row justify-content-end">

                <div class="col-md-4">

                    <table class="table">

                        <tr>

                            <th>Subtotal</th>

                            <td class="text-end">

                                {{ formato(compra.subtotal) }}

                            </td>

                        </tr>

                        <tr>

                            <th>IVA</th>

                            <td class="text-end">

                                {{ formato(compra.iva) }}

                            </td>

                        </tr>

                        <tr>

                            <th>Total</th>

                            <td class="text-end fw-bold">

                                {{ formato(compra.total) }}

                            </td>

                        </tr>

                    </table>

                </div>

            </div>

        </div>

    </div>

</div>

<div
    v-else
    class="text-center mt-5"
>

    Cargando compra...

</div>

</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "../services/api"

const props = defineProps({

    idCompra: Number

})

const emit = defineEmits([

    "volver"

])

const compra = ref(null)

onMounted(async () => {

    const response = await api.get(

        `/compras/${props.idCompra}`

    )

    console.log(response.data)

    compra.value = response.data

})

function formato(valor){

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
async function imprimir() {

    try {

        const response = await api.get(

            `/compras/${props.idCompra}/pdf`,

            {

                responseType: "blob"

            }

        )

        const archivo = window.URL.createObjectURL(

            new Blob([response.data], {

                type: "application/pdf"

            })

        )

        window.open(archivo)

    } catch (e) {

        alert("No fue posible generar el PDF.")

    }

}
</script>
<style scoped>

@media print {

    .btn{

        display:none !important;

    }

    .card{

        border:none !important;

        box-shadow:none !important;

    }

    .card-header{

        border:none;

    }

    body{

        background:white;

    }

}

</style>