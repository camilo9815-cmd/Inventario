<template>
  <section class="panel empty-state">
    <p class="eyebrow">Módulo ERP</p>
    <h2>{{ title }}</h2>
    <p>Este módulo queda listo para conectar su flujo cuando avancemos con el backend.</p>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
})
</script>
