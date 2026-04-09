<script setup lang="ts">
import Navbar from "@views/dashboard/components/Navbar.vue";
import Footer from "@components/layout/footer/Footer.vue";

</script>

<template>
  <Navbar />
  <RouterView/>
  <Footer customClass="bg-black"/>
</template>

<style scoped>

</style>