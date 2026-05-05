<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import ProgressiveImage from "@components/ProgressiveImage.vue";
import Albums from "@views/portfolio/components/Albums.vue";
import Gallery from "@views/portfolio/components/Gallery.vue";

const apiUrl = import.meta.env.VITE_API_URL + '/api'

</script>

<template>
  <div class="relative min-h-screen flex flex-col">
    <ProgressiveImage :src512="`${apiUrl}/uploads/background/portfolio/portfolio-512.webp`"
                      :src1024="`${apiUrl}/uploads/background/portfolio/portfolio-1024.webp`"
                      :src2048="`${apiUrl}/uploads/background/portfolio/portfolio-2048.webp`"
                      alt="Portfolio Background"
                      blur scale
                      class="fixed inset-0 w-full h-full object-cover -z-20"
    />
    <div class="fixed inset-0 bg-linear-180 from-black/0 to-black -z-10"></div>

    <section class="flex-1 pt-28 pb-16 md:pt-48 px-4 md:px-32 text-white">
      <div class="container mx-auto">
        <h1 class="hero-title text-white text-shadow-[0_0_40px_rgba(0,0,0,1)] font-unbounded mb-36 mt-16 md:mt-0">
          <span>Explore</span>
          <span>a brand new</span>
          <span>Horizon</span>
        </h1>
        <Albums/>
        <Gallery/>
      </div>
    </section>
    <Footer/>
  </div>
</template>