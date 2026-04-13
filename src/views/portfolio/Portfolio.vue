<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import ProgressiveImage from "@components/ProgressiveImage.vue";
import Albums from "@views/portfolio/components/Albums.vue";
import Gallery from "@views/portfolio/components/Gallery.vue";
import {Search} from "@lucide/vue"
</script>

<template>
  <div class="relative min-h-screen flex flex-col">
    <ProgressiveImage src512="./src/assets/img/gallery/background/gallery_0001-512.webp"
                      src1024="./src/assets/img/gallery/background/gallery_0001-1024.webp"
                      src2048="./src/assets/img/gallery/background/gallery_0001-2048.webp"
                      alt="Portfolio Background"
                      blur scale
                      class="fixed inset-0 w-full h-full object-cover -z-20"
    />
    <div class="fixed inset-0 bg-linear-180 from-black/0 to-black -z-10"></div>

    <section class="flex-1 pt-28 pb-16 md:pt-48 px-8 md:px-32 text-white">
      <div class="container mx-auto">
        <h1 class="hero-title text-white text-shadow-[0_0_40px_rgba(0,0,0,1)] font-unbounded mb-36 mt-16 md:mt-0">
          <span>Explore</span>
          <span>a brand new</span>
          <span>Horizon</span>
        </h1>
        <div class="flex items-center gap-4 ml-8 mb-8">
          <div :class="['bg-gray-800/30 backdrop-blur-sm text-white',
                        'flex items-center gap-2 px-5 py-4',
                        'border border-gray-500/50 has-focus:border-gray-300/50 transition rounded-full',
                        'shadow-[0_0_15px_rgba(0,0,0,0.25)] has-focus:shadow-[0_0_20px_rgba(127,127,127,0.5)]']">
            <Search class="w-8 h-8"/>
            <input type="text" placeholder="Search" class="bg-transparent outline-none text-lg text-white font-unbounded"/>
          </div>
        </div>
        <Albums/>
        <Gallery/>
      </div>
    </section>
    <Footer/>
  </div>
</template>