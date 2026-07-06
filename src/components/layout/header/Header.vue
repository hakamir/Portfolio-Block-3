<script setup lang="ts">
import {computed, nextTick, ref, watch} from 'vue'
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
    case '/portfolio':
      return 'text-white backdrop-blur-3xl border-b border-white/30 bg-linear-0 from-black/0 to-black/70 text-shadow-[0_0_20px_rgba(0,0,0,1)]'
    default:
      return 'bg-white text-black border-b border-gray-200'
  }
})

// Text color per page
const textColor = computed(() => {
  switch (route.path) {
    case '/':
      return 'white'
    case '/portfolio':
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

// Init scroll opacity
const {backgroundColor, extractRGB} = useScrollOpacity(headerRef, {
  get maxScroll() {
    return scrollOpacityOptions.value?.maxScroll
  },
  get offset() {
    return scrollOpacityOptions.value?.offset
  },
})

// Extract RGB values on route change
watch(() => route.path, () => {
  nextTick(() => extractRGB())
})

// Header style per scroll opacity
const headerStyle = computed(() => {
  if (!scrollOpacityOptions.value) return {}
  return {backgroundColor: backgroundColor.value}
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
          <Logo/>
          <Navbar/>
          <MobileMenu :color="textColor"/>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>

</style>