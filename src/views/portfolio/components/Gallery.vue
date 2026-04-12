<script setup lang="ts">
import {onMounted, onUnmounted, ref} from 'vue'
import {ChevronLeft, ChevronRight} from '@lucide/vue'
import {type Gallery, useGalleriesStore} from "@stores/gallery.ts";

const baseUrl = import.meta.env.VITE_API_URL

const galleriesStore = useGalleriesStore()

onMounted(async () => {
  await galleriesStore.fetchGalleries()
  galleriesStore.galleries.sort((a, b) => a.order - b.order)
  galleriesStore.galleries.forEach(gallery => {
    gallery.images.sort((a, b) => a.order - b.order)
  })
})

const current = ref(0)

const prev = (gallery: Gallery) => current.value = (current.value - 1 + gallery.images.length) % gallery.images.length
const next = (gallery: Gallery) => current.value = (current.value + 1) % gallery.images.length

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
    <div v-for="(gallery, index) in galleriesStore.galleries" :key="index">
      <div class="relative overflow-hidden rounded-3xl aspect-video shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        <transition-group name="fade">
          <img
              v-for="(image, index) in gallery.images"
              v-show="index === current"
              :key="index"
              :src="`${baseUrl}/uploads/gallery/${gallery.slug}/${image.src}`"
              :alt="image.alt"
              class="absolute inset-0 w-full h-full object-cover"
          />
        </transition-group>
      </div>
      <button @click="prev(gallery)"
              class="absolute left-8 top-1/2 -translate-y-1/2 p-4 rounded-full opacity-50 hover:opacity-100 bg-black/30 border border-white/20 text-white backdrop-blur-sm hover:bg-black/50 transition-colors">
        <ChevronLeft :size="24"/>
      </button>
      <button @click="next(gallery)"
              class="absolute right-8 top-1/2 -translate-y-1/2 p-4 rounded-full opacity-50 hover:opacity-100 bg-black/30 border border-white/20 text-white backdrop-blur-sm hover:bg-black/50 transition-colors">
        <ChevronRight :size="24"/>
      </button>
      <div class="flex justify-center gap-2 mt-4">
        <button
            v-for="(_, index) in gallery.images"
            :key="index"
            @click="current = index"
            class="w-2 h-2 rounded-full transition-all duration-300"
            :class="index === current ? 'bg-white scale-125' : 'bg-white/40'"/>
      </div>
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