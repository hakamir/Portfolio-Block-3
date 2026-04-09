<script setup lang="ts">
defineProps({
  title: String
})
</script>

<template>
<div class="px-4 lg:px-12 py-12 backdrop-blur-sm rounded-3xl bg-black/10 border border-white/20 shadow-[0_0_50px_rgba(0,0,0,0.5)] mb-16">
          <h1 class="text-3xl font-unbounded text-shadow-[0_0_10px_rgba(0,0,0,1)]">{{ title }}</h1>
          <div class="flex flex-col mt-16 gap-12 md:px-16">
            <slot />
          </div>
        </div>
</template>

<style scoped>

</style>