<script setup lang="ts">
import Header from "./components/layout/header/Header.vue";
</script>

<template>
  <Header></Header>
  <main class="h-screen overflow-y-scroll scroll-smooth">
    <RouterView/>
  </main>
</template>
