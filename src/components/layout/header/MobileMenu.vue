<script setup lang="ts">

</script>

<template>
  <div class="block md:hidden ms-auto z-10">
    <button id="menu-button" class="menu-button" type="button" aria-label="Menu button">
      <span class="line"></span>
      <span class="line"></span>
      <span class="line"></span>
    </button>
  </div>
  <div id="mobile-menu"
       class="hidden absolute top-0 right-0 bg-black px-4 pt-16 pb-8 rounded-bl-2xl border-white border-l border-b">
    <ul>
      <li><a class="nav-item font-unbounded" href="/block1-frontend/">HOME</a></li>
      <li><a class="nav-item font-unbounded" href="/block1-frontend/pages/portfolio">PORTFOLIO</a></li>
      <li><a class="nav-item font-unbounded" href="/block1-frontend/pages/contact">CONTACT</a></li>
    </ul>
  </div>
</template>

<style scoped>

</style>