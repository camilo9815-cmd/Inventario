<template>

<div class="card mt-3">

    <div class="card-header">
        <strong>Detalle</strong>
    </div>

    <div class="table-responsive">

        <table class="table table-hover align-middle mb-0">

            <thead>

                <tr>

                    <th>Código</th>

                    <th>Producto</th>

                    <th width="120">Cantidad</th>

                    <th width="150">Costo</th>

                    <th width="120">IVA %</th>

                    <th>Base</th>

                    <th>IVA</th>

                    <th>Total</th>

                    <th width="80"></th>

                </tr>

            </thead>

            <tbody>

                <tr
                    v-for="(item,index) in detalle"
                    :key="index"
                >

                    <td>{{ item.codigo }}</td>

                    <td>{{ item.nombre }}</td>

                    <td>

                        <input

                            class="form-control"

                            type="number"

                            min="1"

                            v-model.number="item.cantidad"

                            @input="calcular(item)"

                        >

                    </td>

                    <td>

                        <input

                            class="form-control"

                            type="number"

                            min="0"

                            step="0.01"

                            v-model.number="item.costo_unitario"

                            @input="calcular(item)"

                        >

                    </td>

                    <td>
                        <input
                            class="form-control"
                            type="number"
                            min="0"
                            max="100"
                            step="0.01"
                            v-model.number="item.porcentaje_iva"
                            @input="calcular(item)"
                        >

                    </td>

                    <td>

                        {{ formato(item.base) }}

                    </td>

                    <td>

                        {{ formato(item.iva) }}

                    </td>

                    <td>

                        {{ formato(item.total) }}

                    </td>

                    <td>

                        <button

                            class="btn btn-danger btn-sm"

                            @click="eliminar(index)"

                        >

                            X

                        </button>

                    </td>

                </tr>

            </tbody>

        </table>

    </div>

</div>

</template>

<script setup>

const props = defineProps({

    detalle:Array

})

const emit = defineEmits([

    "update:detalle"

])

function calcular(item){

    item.base = item.cantidad * item.costo_unitario

    item.iva = item.base * (item.porcentaje_iva / 100)

    item.total = item.base + item.iva

    emit("update:detalle", props.detalle)

}

function eliminar(index){

    props.detalle.splice(index,1)

    emit(

        "update:detalle",

        props.detalle

    )

}

function formato(valor){

    return new Intl.NumberFormat(

        "es-CO",

        {

            style:"currency",

            currency:"COP",

            maximumFractionDigits:0

        }

    ).format(valor??0)

}

</script>