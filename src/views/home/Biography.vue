<script setup lang="ts">
import {useBiographyStore} from "@stores/biography.ts";
import {onMounted} from "vue";
import {storeToRefs} from "pinia";
import ProgressiveImage from "@components/ProgressiveImage.vue";
import {useBackgroundStore} from "@stores/background.ts";

const biographyStore = useBiographyStore()
let {biography} = storeToRefs(biographyStore)

const backgroundStore = useBackgroundStore()
const {biographyBg} = storeToRefs(backgroundStore)

onMounted(async () => {
  await biographyStore.fetchBiography()
})

</script>

<template>
  <section v-if="biography" class="relative sm:min-h-screen bg-neutral-300 sm:snap-start"
           aria-labelledby="biography-title">
    <div class="grid grid-cols-1 md:landscape:grid-cols-1 lg:landscape:grid-cols-2 min-h-screen">
      <div class="lg:sticky lg:top-0 lg:h-screen lg:w-full">
        <ProgressiveImage :src512="biographyBg.sm"
                          :src1024="biographyBg.md"
                          :src2048="biographyBg.lg"
                          alt="Taylor Spark portrait"
                          :responsive=true
                          class="w-full h-full object-cover"
                          role="presentation"/>
        <div
            class="hidden sm:block absolute top-0 right-0 h-full w-0.5 bg-linear-to-r from-neutral-300/0 to-neutral-300"></div>
      </div>
      <div class="col-span-1 md:col-start-2 text-black px-8 lg:px-14 pt-8 pb-20 sm:pt-32">
        <div class="pb-6">
          <h2 id="biography-title" class="font-unbounded text-3xl sm:text-5xl">{{ biography.title }}</h2>
          <div v-for="section in biography.sections">
            <h3 class="font-unbounded text-xl sm:text-2xl pt-16">{{ section.title }}</h3>
            <p class="pt-2 lg:pl-4 text-md! leading-relaxed" v-for="paragraph in section.paragraphs">{{ paragraph }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>

</style>