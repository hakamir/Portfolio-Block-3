<script setup lang="ts">
import Hero from "./Hero.vue";
import Biography from "./Biography.vue";
import Footer from "@components/layout/footer/Footer.vue";
</script>

<template>
  <Hero></Hero>
  <Biography></Biography>
  <section class="relative min-h-screen bg-neutral-300 snap-start flex flex-col">
    <div class="container mx-auto px-4 pt-32 pb-20 flex-1 flex items-center">
      <div>
        <h2 class="text-3xl font-bold mb-4 font-unbounded">Contact Me</h2>
        <p class="text-lg pb-4">Ready to collaborate? Let's discuss your project and how I can contribute.</p>
        <RouterLink to="/contact"
                    class="bg-black text-white px-6 py-3 font-unbounded rounded transition-all duration-300 hover:bg-neutral-700 inline-block">
          Contact me now!
        </RouterLink>
      </div>
    </div>
    <Footer></Footer>
  </section>
</template>

<style scoped>

</style>