<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { CirclePlay, CirclePause } from '@lucide/vue'
import { useAudioPlayerStore } from "@stores"

const props = defineProps<{ src: string, className?: string }>()

const playerStore = useAudioPlayerStore()
const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)

const togglePlay = () => {
  if (!audioRef.value) return
  if (isPlaying.value) {
    playerStore.pause(audioRef.value)
    audioRef.value.currentTime = 0
    isPlaying.value = false
  } else {
    playerStore.play(audioRef.value)
    isPlaying.value = true
  }
}

const onPause = () => { isPlaying.value = false }

onMounted(() => audioRef.value?.addEventListener('pause', onPause))
onBeforeUnmount(() => audioRef.value?.removeEventListener('pause', onPause))
</script>

<template>
  <button @click="togglePlay" :class="[props.className]">
    <CirclePlay v-if="!isPlaying" class="max-w-6 h-6 text-blue-700/70"/>
    <CirclePause v-else class="w-6 h-6 text-red-700/70"/>
  </button>
  <audio ref="audioRef" :src="props.src" preload="none"/>
</template>