import { createRouter, createWebHistory } from "vue-router";

const routes = [

    {
        path: "/",
        redirect: "/dashboard"
    },

    {
        path: "/dashboard",
        component: () => import("../views/DashboardView.vue")
    },

    {
        path: "/productos",
        component: () => import("../views/ProductosView.vue")
    },

    {
        path: "/proveedores",
        component: () => import("../views/ProveedoresView.vue")
    },

    {
        path: "/clientes",
        component: () => import("../views/ClientesView.vue")
    },

    {
        path: "/inventario",
        component: () => import("../views/InventarioView.vue")
    },

    {
        path: "/gastos",
        component: () => import("../views/GastosView.vue")
    },



    {
        path: "/compras",
        name: "ComprasConsulta",
        component: () => import("../views/ComprasConsultaView.vue")
    },

    {
        path: "/compras/nueva",
        name: "CompraNueva",
        component: () => import("../views/ComprasNuevaView.vue")
    },

    {
        path: "/ventas",
        name: "VentasConsulta",
        component: () => import("../views/VentasConsultaView.vue")
    },

    {
        path: "/ventas/nueva",
        name: "VentaNueva",
        component: () => import("../views/VentasNuevaView.vue")
    },

    {
        path: "/ventas/:id",
        name: "VentaDetalle",
        component: () => import("../views/VentaDetalleView.vue"),
        props: route => ({
            idVenta: Number(route.params.id)
        })
    },{
    path:'/punto-equilibrio',
    name:'PuntoEquilibrio',
    component:PuntoEquilibrioView
}

];

export default createRouter({

    history: createWebHistory(),

    routes

});
