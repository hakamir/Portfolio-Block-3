<script setup lang="ts">
import {onMounted, onUnmounted, ref} from 'vue'
import {ChevronLeft, ChevronRight} from '@lucide/vue'

const baseUrl = import.meta.env.VITE_API_URL

const images = [
  {src: `${baseUrl}/uploads/gallery/gallery_0001.webp`, alt: 'gallery'},
  {src: `${baseUrl}/uploads/gallery/gallery_0002.webp`, alt: 'gallery'},
  {src: `${baseUrl}/uploads/gallery/gallery_0003.webp`, alt: 'gallery'},
  {src: `${baseUrl}/uploads/gallery/gallery_0004.webp`, alt: 'gallery'},
]

const current = ref(0)

const prev = () => current.value = (current.value - 1 + images.length) % images.length
const next = () => current.value = (current.value + 1) % images.length

let autoplay: number;
const startAutoplay = () => autoplay = setInterval(next, 3000)
const stopAutoplay = () => clearInterval(autoplay)

onMounted(() => startAutoplay())
onUnmounted(() => stopAutoplay())
</script>

<template>
  <div class="relative w-full mx-auto" @mouseenter="stopAutoplay" @mouseleave="startAutoplay">
    <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">
      Gallery
    </h2>
    <div class="relative overflow-hidden rounded-3xl aspect-video shadow-[0_0_50px_rgba(0,0,0,0.5)]">
      <transition-group name="fade">
        <img
            v-for="(image, index) in images"
            v-show="index === current"
            :key="index"
            :src="image.src"
            :alt="image.alt"
            class="absolute inset-0 w-full h-full object-cover"
        />
      </transition-group>
    </div>
    <button @click="prev"
            class="absolute left-8 top-1/2 -translate-y-1/2 p-4 rounded-full opacity-50 hover:opacity-100 bg-black/30 border border-white/20 text-white backdrop-blur-sm hover:bg-black/50 transition-colors">
      <ChevronLeft :size="24"/>
    </button>
    <button @click="next"
            class="absolute right-8 top-1/2 -translate-y-1/2 p-4 rounded-full opacity-50 hover:opacity-100 bg-black/30 border border-white/20 text-white backdrop-blur-sm hover:bg-black/50 transition-colors">
      <ChevronRight :size="24"/>
    </button>
    <div class="flex justify-center gap-2 mt-4">
      <button
          v-for="(_, index) in images"
          :key="index"
          @click="current = index"
          class="w-2 h-2 rounded-full transition-all duration-300"
          :class="index === current ? 'bg-white scale-125' : 'bg-white/40'"/>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>