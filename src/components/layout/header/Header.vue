<script setup lang="ts">

import Logo from "./Logo.vue";
import Navbar from "./Navbar.vue";
import MobileMenu from "./MobileMenu.vue";
</script>

<template>
  <header id="header" class="fixed top-0 z-50 w-full ">
    <div class="py-4">
      <div class="mx-auto px-4">
        <div class="flex items-center md:px-10 md:py-4">
          <Logo></Logo>
          <Navbar></Navbar>
          <MobileMenu></MobileMenu>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>

</style>