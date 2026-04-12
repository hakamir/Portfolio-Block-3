<script setup lang="ts">
import AudioSection from "@views/dashboard/works/Components/AudioSection.vue";
import GallerySection from "@views/dashboard/works/Components/GallerySection.vue";

</script>

<template>

  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-8 md:px-32 flex flex-col gap-4">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Works</h1>
    <AudioSection />
    <GallerySection />
  </section>
</template>

<style scoped>

</style>