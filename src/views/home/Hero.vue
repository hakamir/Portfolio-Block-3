<script setup lang="ts">
import { vWave } from "@directives/wave.js";
</script>

<template>
  <section
      class="grid grid-rows-2 sm:relative bg-black text-white overflow-hidden min-h-screen h-screen sm:flex sm:items-center sm:snap-start">
    <!-- Hero Image -->
    <div class="sm:absolute sm:right-0 sm:top-0 sm:w-2/3 sm:h-full z-0">
      <picture>
        <source media="(max-width: 640px)" srcset="../../assets/img/hero/hero-1/hero-1-512.webp">
        <source media="(max-width: 1280px)" srcset="../../assets/img/hero/hero-1/hero-1-1024.webp">
        <img src="../../assets/img/hero/hero-1/hero-1-2048.webp"
             alt="Block1 Logo"
             class="w-full h-full object-cover">
      </picture>
      <div class="hidden sm:block absolute top-0 left-0 h-full w-50 bg-linear-to-l from-black/0 to-black"></div>
    </div>
    <!-- Hero -->
    <div class="relative px-5 container mx-auto py-8 z-20 sm:snap-center">
      <div class="pb-6">
        <h1 class="hero-title font-unbounded"><span>Let's</span><span>Make Music</span>
          <span>Together</span>
        </h1>
      </div>
      <div class="pl-8">
        <div class="lg:w-1/3">
          <p>I bring energy, precision, and passion to live performances—ready to elevate your next
            show.</p>
        </div>
        <div class="pt-6">
          <button class="btn-primary wave-btn bg-primary text-black group" v-wave>
            Listen now
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>

</style>