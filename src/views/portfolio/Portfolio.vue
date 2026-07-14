<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import ProgressiveImage from "@components/ProgressiveImage.vue";
import Albums from "@views/portfolio/components/Albums.vue";
import Gallery from "@views/portfolio/components/Gallery.vue";
import {useBackgroundStore} from "@stores/background.ts";
import {storeToRefs} from "pinia";

const backgroundStore = useBackgroundStore()
const {portfolioBg} = storeToRefs(backgroundStore)

</script>

<template>
  <div class="relative min-h-screen flex flex-col">
    <ProgressiveImage :src512="portfolioBg.sm"
                      :src1024="portfolioBg.md"
                      :src2048="portfolioBg.lg"
                      alt="Portfolio Background"
                      blur scale
                      class="fixed inset-0 w-full h-full object-cover -z-20"
                      role="presentation"
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