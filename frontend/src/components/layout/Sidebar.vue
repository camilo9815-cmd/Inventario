<template>

<aside class="sidebar">

    <div class="brand">

        <div class="brand-mark">
            JF
        </div>

        <div>

            <strong>Inventario JF</strong>

            <span>Administración</span>

        </div>

    </div>

    <nav class="menu">

        <div
            v-for="item in menu"
            :key="item.label"
            class="menu-item"
        >

            <!-- ITEM NORMAL -->

            <button

                v-if="!item.children"

                class="nav-link"

                :class="{active:modelValue===item.key}"

                @click="$emit('update:modelValue',item.key)"

            >

                <i :class="item.icon"></i>

                <span>{{ item.label }}</span>

            </button>

            <!-- ITEM CON SUBMENU -->

            <div v-else>

                <button

                    class="nav-link"

                    @click="toggle(item.label)"

                >

                    <div>

                        <i :class="item.icon"></i>

                        <span>{{ item.label }}</span>

                    </div>

                    <i

                        class="bi"

                        :class="

                            abierto[item.label]

                            ? 'bi-chevron-down'

                            : 'bi-chevron-right'

                        "

                    ></i>

                </button>

                <transition name="submenu">

                    <div

                        v-show="abierto[item.label]"

                        class="submenu"

                    >

                        <button

                            v-for="sub in item.children"

                            :key="sub.key"

                            class="submenu-link"

                            :class="{active:modelValue===sub.key}"

                            @click="$emit('update:modelValue',sub.key)"

                        >

                            {{ sub.label }}

                        </button>

                    </div>

                </transition>

            </div>

        </div>

    </nav>

</aside>

</template>

<script setup>

import { reactive } from "vue"

defineProps({

    menu:Array,

    modelValue:String

})

defineEmits([

    "update:modelValue"

])

const abierto=reactive({})

function toggle(nombre){

    abierto[nombre]=!abierto[nombre]

}

</script>

<style scoped>

.sidebar{

    width:270px;

    background:#1f2937;

    color:white;

    height:100vh;

    overflow-y:auto;

}

.brand{

    display:flex;

    gap:15px;

    align-items:center;

    padding:20px;

    border-bottom:1px solid rgba(255,255,255,.1);

}

.brand-mark{

    width:45px;

    height:45px;

    border-radius:10px;

    background:#0d6efd;

    display:flex;

    align-items:center;

    justify-content:center;

    font-weight:bold;

}

.menu{

    padding:15px;

}

.nav-link{

    width:100%;

    border:none;

    background:none;

    color:white;

    padding:12px;

    display:flex;

    justify-content:space-between;

    align-items:center;

    border-radius:8px;

    margin-bottom:4px;

    cursor:pointer;

}

.nav-link:hover{

    background:#374151;

}

.nav-link.active{

    background:#2563eb;

}

.nav-link>div{

    display:flex;

    gap:10px;

    align-items:center;

}

.submenu{

    padding-left:18px;

}

.submenu-link{

    width:100%;

    background:none;

    border:none;

    color:#d1d5db;

    text-align:left;

    padding:10px;

    border-radius:6px;

    cursor:pointer;

}

.submenu-link:hover{

    background:#374151;

}

.submenu-link.active{

    background:#2563eb;

    color:white;

}

.submenu-enter-active,

.submenu-leave-active{

    transition:.25s;

}

.submenu-enter-from,

.submenu-leave-to{

    opacity:0;

    transform:translateY(-8px);

}

</style>