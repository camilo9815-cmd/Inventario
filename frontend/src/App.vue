<template>
  <LoginView
    v-if="!token"
    @authenticated="onAuthenticated"
  />

  <div
    v-else
    class="app-shell"
  >
    <Sidebar
    :menu="menu"
    v-model="activeView"
    />

    <main class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">Panel operativo</p>
          <h1>{{ currentTitle }}</h1>
        </div>

        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="logout"
        >
          Salir
        </button>
      </header>

      <DashboardView v-if="activeView === 'dashboard'" />
      <ProductosView v-else-if="activeView === 'productos'" />
      <ProveedoresView v-else-if="activeView === 'proveedores'" />
      <ClientesView v-else-if="activeView === 'clientes'" />
      <InventarioView v-else-if="activeView === 'inventario'" />
      <GastosView v-else-if="activeView === 'gastos'" />
      <ComprasView
        v-else-if="activeView === 'compras' || activeView === 'compras-editar'"
        :idCompra="activeView === 'compras-editar' ? idCompraSeleccionada : null"
        @consulta="activeView='compras-consulta'"
      />
      <ComprasConsultaView
          v-else-if="activeView === 'compras-consulta'"
          @ver="abrirDetalleCompra"
          @editar="editarCompra"
      />
      <CompraDetalleView
          v-else-if="activeView === 'compras-detalle'"
          :idCompra="idCompraSeleccionada"
          @volver="activeView='compras-consulta'"
      />
      <VentasNuevaView
        v-else-if="activeView === 'ventas' || activeView === 'ventas-editar'"
        :idVenta="activeView === 'ventas-editar' ? idVentaSeleccionada : null"
        @consulta="activeView='ventas-consulta'"
      />
      <VentasConsultaView
        v-else-if="activeView === 'ventas-consulta'"
        @nueva="activeView='ventas'"
        @ver="abrirDetalleVenta"
        @editar="editarVenta"
      />
      <VentaDetalleView
        v-else-if="activeView === 'ventas-detalle'"
        :idVenta="idVentaSeleccionada"
        @volver="activeView='ventas-consulta'"
      />
      <CarteraClientesView v-else-if="activeView === 'cartera-clientes'" />
      <CarteraProveedoresView v-else-if="activeView === 'cartera-proveedores'" />
      <PuntoEquilibrioView v-else-if="activeView === 'punto-equilibrio'" />
      <PlaceholderView
        v-else
        :title="currentTitle"
      />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import DashboardView from './views/DashboardView.vue'
import LoginView from './views/LoginView.vue'
import PlaceholderView from './views/PlaceholderView.vue'
import ProductosView from './views/ProductosView.vue'
import ProveedoresView from './views/ProveedoresView.vue'
import ClientesView from './views/ClientesView.vue'
import InventarioView from './views/InventarioView.vue'
import GastosView from './views/GastosView.vue'
import ComprasView from './views/ComprasNuevaView.vue'
import ComprasConsultaView from './views/ComprasConsultaView.vue'
import CompraDetalleView from './views/CompraDetalleView.vue'
import VentasNuevaView from './views/VentasNuevaView.vue'
import VentasConsultaView from './views/VentasConsultaView.vue'
import VentaDetalleView from './views/VentaDetalleView.vue'
import Sidebar from "./components/layout/Sidebar.vue"
import CarteraClientesView from './views/CarteraClientesView.vue'
import CarteraProveedoresView from './views/CarteraProveedoresView.vue'
import PuntoEquilibrioView from './views/PuntoEquilibrioView.vue'


const token = ref(localStorage.getItem('erp_token'))
const activeView = ref('dashboard')

const menu = [

    {
        key: "dashboard",
        label: "Dashboard",
        icon: "01"
    },
     {
        key: "productos",
        label: "Productos",
        icon: "02"
    },
    {
        key: "inventario",
        label: "Inventario",
        icon: "02"
    },

    {
        key: "compras",
        label: "Compras",
        icon: "03",
        children: [

            {
                key: "compras",
                label: "Nueva Compra"
            },

            {
                key: "compras-consulta",
                label: "Consultar Compras"
            }

        ]
    },

    {
        key: "ventas",
        label: "Ventas",
        icon: "04",
        children: [

            {
                key: "ventas",
                label: "Nueva Venta"
            },

            {
                key: "ventas-consulta",
                label: "Consultar Ventas"
            }

        ]
    },

    {
        key: "terceros",
        label: "Terceros",
        icon: "05",
        children: [

            {
                key: "clientes",
                label: "Clientes"
            },

            {
                key: "proveedores",
                label: "Proveedores"
            }

        ]
    },

    {
        key: "cartera",
        label: "Cartera",
        icon: "06",
        children: [

            {
                key: "cartera-clientes",
                label: "Cartera Clientes"
            },

            {
                key: "cartera-proveedores",
                label: "Cartera Proveedores"
            }

        ]
    },

    {
        key: "tesoreria",
        label: "Tesorería",
        icon: "06",
        children: [

            {
                key: "gastos",
                label: "Gastos"
            },

            {
                key: "medios-pago",
                label: "Medios de Pago"
            }

        ]
    },
    {
    key:'punto-equilibrio',
    label:'Punto de Equilibrio'
}

]

const currentTitle = computed(() => {
  for (const item of menu) {
    if (item.key === activeView.value) return item.label
    if (item.children) {
      const sub = item.children.find(c => c.key === activeView.value)
      if (sub) return sub.label
    }
  }
  return 'Dashboard'
})

function onAuthenticated(newToken) {
  token.value = newToken
}

function logout() {
  localStorage.removeItem('erp_token')
  token.value = ''
  activeView.value = 'dashboard'
}

const idCompraSeleccionada = ref(null)
const idVentaSeleccionada = ref(null)

function abrirDetalleCompra(id){

    idCompraSeleccionada.value = id

    activeView.value = "compras-detalle"

}

function abrirDetalleVenta(id){

    idVentaSeleccionada.value = id

    activeView.value = "ventas-detalle"

}

function editarCompra(id) {
  idCompraSeleccionada.value = id
  activeView.value = 'compras-editar'
}

function editarVenta(id) {
  idVentaSeleccionada.value = id
  activeView.value = 'ventas-editar'
}
</script>
