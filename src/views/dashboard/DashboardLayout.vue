<script setup lang="ts">
import Navbar from "@views/dashboard/components/Navbar.vue";
import Footer from "@components/layout/footer/Footer.vue";

</script>

<template>
  <div class="min-h-screen flex flex-col">
  <Navbar/>
    <RouterView/>
    <Footer class="mt-auto" customClass="bg-black"/>
  </div>
</template>

<style scoped>

</style>