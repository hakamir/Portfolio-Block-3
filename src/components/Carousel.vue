<script setup lang="ts">
import {ref, onMounted, onUnmounted, watch} from 'vue'
import {ChevronLeft, ChevronRight} from '@lucide/vue'
import type {Image} from "@stores/gallery.ts";

const props = defineProps<{
  images: Image[]
  baseSrc?: string
  autoplay?: boolean
  autoplayDelay?: number
}>()

const current = ref(0)

const prev = () => current.value = (current.value - 1 + props.images.length) % props.images.length
const next = () => current.value = (current.value + 1) % props.images.length

let autoplayInterval: ReturnType<typeof setInterval>

const startAutoplay = () => {
  if (!props.autoplay) return
  autoplayInterval = setInterval(next, props.autoplayDelay ?? 4000)
}
const stopAutoplay = () => clearInterval(autoplayInterval)

onMounted(() => startAutoplay())
onUnmounted(() => stopAutoplay())

const preloadImg = (src: string) => {
  const img = new Image()
  img.src = src
}

watch(current, (newIndex) => {
  const nextIndex = (newIndex + 1) % props.images.length
  const nextSrc = props.baseSrc ? `${props.baseSrc}/${props.images[nextIndex].src}` : props.images[nextIndex].src
  preloadImg(nextSrc)
})

</script>

<template>
  <div class="relative w-full" @mouseenter="stopAutoplay" @mouseleave="startAutoplay">
    <div class="relative overflow-hidden rounded-3xl aspect-video shadow-[0_0_50px_rgba(0,0,0,0.5)] group">
      <transition-group name="fade" mode="out-in">
        <img
            :key="current"
            :src="baseSrc ? `${baseSrc}/${images[current].src}` : images[current].src"
            :alt="images[current].alt"
            class="absolute inset-0 w-full h-full object-cover"
        />
      </transition-group>
      <div class="absolute inset-0 z-10 items-end p-6 pointer-events-none flex flex-col">
        <span class="text-white opacity-40 text-2xl text-shadow-[0_0_20px_rgba(0,0,0,1)] font-unbounded group-hover:opacity-100 transition-opacity">
          {{ images[current]?.title }}
        </span>
        <div>
          <span class="text-white opacity-20 font-light text-sm text-shadow-[0_0_20px_rgba(0,0,0,1)] font-unbounded group-hover:opacity-80 transition-opacity">
            {{ images[current]?.location }} - {{ new Date(images[current]?.date).toLocaleDateString() }}
          </span>
        </div>
      </div>
    </div>

    <button @click="prev"
            class="absolute left-8 top-1/2 -translate-y-1/2 p-4 rounded-full opacity-50 hover:opacity-100 bg-black/30 border border-white/20 text-white backdrop-blur-sm hover:bg-black/50 transition-colors" aria-label="Previous image">
      <ChevronLeft :size="24"/>
    </button>
    <button @click="next"
            class="absolute right-8 top-1/2 -translate-y-1/2 p-4 rounded-full opacity-50 hover:opacity-100 bg-black/30 border border-white/20 text-white backdrop-blur-sm hover:bg-black/50 transition-colors" aria-label="Next image">
      <ChevronRight :size="24"/>
    </button>

    <div class="flex justify-center gap-2 mt-4">
      <button
          v-for="(_, index) in images"
          :key="index"
          @click="current = index"
          class="w-2 h-2 rounded-full transition-all duration-300"
          :class="index === current ? 'bg-white scale-125' : 'bg-white/40'"
          aria-label="Select image">
      </button>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease-in-out;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>