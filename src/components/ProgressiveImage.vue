<script setup lang="ts">
import { ref, onMounted, useTemplateRef } from 'vue'

const props = defineProps<{
  src512: string
  src1024: string
  src2048: string
  alt: string
  class?: string
  responsive?: boolean
  blur?: boolean
  scale?: boolean
}>()

const isLoaded = ref(false)
const imgRef = useTemplateRef('imgRef')

onMounted(async () => {
  try {
    if (imgRef.value?.complete) {
      isLoaded.value = true
      return
    }
    imgRef.value?.addEventListener('load', () => {
      isLoaded.value = true
    })
  } catch {
    isLoaded.value = true
  }
})
</script>

<template>
  <picture v-if="responsive">
    <source media="(max-width: 640px)" :srcset="src512">
    <source media="(max-width: 1280px)" :srcset="src1024">
    <img
      ref="imgRef"
      :src="src2048"
      :alt="alt"
      :class="[props.class, {
        'blur-sm': blur && !isLoaded,
        'blur-none': blur && isLoaded,
        'scale-105': scale && !isLoaded,
        'scale-100': scale && isLoaded,
        'transition-[filter, transform]': blur || scale,
        'duration-700 ease-in-out': blur || scale,
      }]"
    />
  </picture>

  <img
    v-else
    ref="imgRef"
    :src="src2048"
    :alt="alt"
    :class="[props.class, {
      'blur-sm': blur && !isLoaded,
      'blur-none': blur && isLoaded,
      'scale-105': scale && !isLoaded,
      'scale-100': scale && isLoaded,
      'transition-[filter, transform]': blur || scale,
      'duration-700 ease-in-out': blur || scale,
    }]"
  />
</template>