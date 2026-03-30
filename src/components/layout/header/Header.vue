<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Logo from "./Logo.vue";
import Navbar from "./Navbar.vue";
import MobileMenu from "./MobileMenu.vue";
import { vScrollOpacity, type ScrollOpacityOptions } from "../../../directives/scrollOpacity.ts";

const route = useRoute()

const headerClasses = computed(() => {
  switch (route.path) {
    case '/':
      return 'bg-black text-white'
    case '/portfolio':
      return 'bg-white text-black'
    case '/contact':
      return 'bg-white text-black'
    default:
      return 'bg-white text-black'
  }
})

const textColor = computed(() => {
  switch (route.path) {
    case '/':
      return 'white'
    default:
      return 'black'
  }
})

const scrollOpacityOptions = computed<ScrollOpacityOptions | null>(() => {
  switch (route.path) {
    case '/':
      return {
        maxScroll: 500,
        offset: 200,
        scrollContainer: 'main'
      }
    default:
      return null
  }
})

</script>

<template>
  <header id="header"
          :class="['fixed top-0 z-50 w-full', headerClasses]"
          v-scroll-opacity="scrollOpacityOptions"
  >
    <div class="py-4">
      <div class="mx-auto px-4">
        <div class="flex items-center md:px-10 md:py-4">
          <Logo :color="textColor" />
          <Navbar :color="textColor" />
          <MobileMenu :color="textColor" />
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>

</style>