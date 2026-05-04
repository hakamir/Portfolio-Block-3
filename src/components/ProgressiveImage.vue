<script setup lang="ts">
import { ref, onMounted } from 'vue'

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

const currentSrc = ref(props.src512)
const isLoaded = ref(false)

const loadImage = (src: string) => {
  return new Promise<void>((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = () => reject()
    img.src = src
    if (img.complete) resolve()
  })
}

onMounted(async () => {
  try {
    await loadImage(props.src1024)
    currentSrc.value = props.src1024
    await loadImage(props.src2048)
    currentSrc.value = props.src2048
    isLoaded.value = true
  } catch (e) {
    isLoaded.value = true
  }
})
</script>

<template>
  <picture v-if="responsive">
    <source media="(max-width: 640px)" :srcset="src512">
    <source media="(max-width: 1280px)" :srcset="src1024">
    <img
      :src="currentSrc"
      :alt="alt"
      :class="[props.class, {
        'blur-sm': blur && !isLoaded,
        'blur-none': blur && isLoaded,
        'scale-105': scale && !isLoaded,
        'scale-100': scale && isLoaded,
        'transition-[filter, transform]': blur || scale,
        'duration-700 ease-in-out': blur || scale,
      }]"
      fetchpriority="high"
    />
  </picture>

  <img
    v-else
    :src="currentSrc"
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