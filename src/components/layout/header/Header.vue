<script setup lang="ts">
import {computed, ref} from 'vue'
import {useRoute} from 'vue-router'
import Logo from "./Logo.vue";
import Navbar from "./Navbar.vue";
import MobileMenu from "./MobileMenu.vue";
import useScrollOpacity from "@composables/animations/scrollOpacity/useScrollOpacity.ts";

const route = useRoute()
const headerRef = ref<HTMLElement | null>(null)

// Header style per page
const headerClasses = computed(() => {
  switch (route.path) {
    case '/':
      return 'bg-black text-white'
    default:
      return 'bg-white text-black'
  }
})

// Text color per page
const textColor = computed(() => {
  switch (route.path) {
    case '/':
      return 'white'
    default:
      return 'black'
  }
})

// Scroll opacity params per page
const scrollOpacityOptions = computed(() => {
  switch (route.path) {
    case '/':
      return {maxScroll: 500, offset: 200}
    default:
      return null
  }
})

// Use scroll opacity composable if scroll opacity options are defined
const scrollOpacity = scrollOpacityOptions.value ? useScrollOpacity(headerRef, scrollOpacityOptions.value) : null

// Dynamic header style based on scroll opacity
const headerStyle = computed(() => {
  if (scrollOpacity) {
    return { backgroundColor: scrollOpacity.backgroundColor.value }
  }
  return {}
})

</script>

<template>
  <header id="header"
          :class="['fixed top-0 z-50 w-full', headerClasses]"
          :style="headerStyle"
  >
    <div class="py-4">
      <div class="mx-auto px-4">
        <div class="flex items-center md:px-10 md:py-4">
          <Logo :color="textColor"/>
          <Navbar :color="textColor"/>
          <MobileMenu :color="textColor"/>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>

</style>