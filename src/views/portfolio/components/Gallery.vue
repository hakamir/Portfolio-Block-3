<script setup lang="ts">
import {onMounted} from 'vue'
import {useGalleriesStore} from "@stores/gallery.ts";
import Carousel from "@components/Carousel.vue";

const baseUrl = import.meta.env.VITE_API_URL

const galleriesStore = useGalleriesStore()

onMounted(async () => {
  await galleriesStore.fetchGalleries()
})
</script>

<template>
  <div class="relative w-full mx-auto">
    <h2 class="font-unbounded text-3xl md:text-5xl mb-8 text-shadow-[0_0_20px_rgba(0,0,0,1)]">
      Gallery
    </h2>
    <div v-for="(gallery, index) in galleriesStore.galleries" :key="index">
      <Carousel
          :images="gallery.images"
          :baseSrc="`${baseUrl}/uploads/gallery/${gallery.slug}`"
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