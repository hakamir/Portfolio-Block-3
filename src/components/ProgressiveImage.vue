<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  src512: string
  src1024: string
  src2048: string
  alt: string
  class?: string
}>()

const currentSrc = ref(props.src512)
const isLoaded = ref(false)

function loadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
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
  <img
    :src="currentSrc"
    :alt="alt"
    :class="[props.class, { 'blur-lg scale-105': !isLoaded, 'blur-0 scale-100': isLoaded }]"
    class="transition-all duration-700 ease-in-out"
  />
</template>