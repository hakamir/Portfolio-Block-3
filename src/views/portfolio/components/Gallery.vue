<script setup lang="ts">
import {onMounted} from 'vue'
import {useGalleriesStore} from "@stores/gallery.ts";
import Carousel from "@components/Carousel.vue";

const baseUrl = import.meta.env.VITE_API_URL + '/api'

const galleriesStore = useGalleriesStore()

onMounted(async () => {
  await galleriesStore.fetchGalleries()
})
</script>

<template>
  <div class="relative w-full mx-auto">
    <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">
      <span v-if="galleriesStore.galleries.length === 1">Gallery</span>
      <span v-else-if="galleriesStore.galleries.length > 1">Galleries</span>
      <span v-else>No gallery found</span>
    </h2>
    <div v-for="(gallery, index) in galleriesStore.galleries" :key="index">
      <h3 class="font-unbounded text-xl md:text-2xl ml-4 mb-4 sm:mb-8">{{ gallery.title }}</h3>
      <Carousel
          :images="gallery.images"
          :baseSrc="`${baseUrl}/upload/gallery/${gallery.slug}`"
          autoplay
          :autoplay-delay="5000"
      />
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