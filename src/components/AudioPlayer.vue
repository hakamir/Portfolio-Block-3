<script setup lang="ts">
import { ref } from 'vue'
import { Play, Pause } from '@lucide/vue'

const props = defineProps<{
  src: string
  title: string
  subtitle: string
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const progress = ref(0) // Progress in percentage
const currentTime = ref('0:00')
const duration = ref('0:00')

// Format time in mm:ss format
const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// Toggle play/pause
const togglePlay = () => {
  if (!audioRef.value) return
  isPlaying.value ? audioRef.value.pause() : audioRef.value.play()
  isPlaying.value = !isPlaying.value
}

// Calculate progress in percentage
const onTimeUpdate = () => {
  if (!audioRef.value) return
  progress.value = (audioRef.value.currentTime / audioRef.value.duration) * 100
  currentTime.value = formatTime(audioRef.value.currentTime)
}

// Get song duration when audio is loaded
const onLoaded = () => {
  if (!audioRef.value) return
  duration.value = formatTime(audioRef.value.duration)
}

// Seek to a specific time in the song using click event on the seek bar
const seek = (event: MouseEvent) => {
  if (!audioRef.value) return
  const bar = event.currentTarget as HTMLElement
  const ratio = event.offsetX / bar.offsetWidth
  audioRef.value.currentTime = ratio * audioRef.value.duration
}
</script>

<template>
  <div class="flex items-center gap-4">
    <button @click="togglePlay"
            class="w-12 h-12 rounded-full bg-white text-black flex items-center justify-center hover:bg-neutral-200 transition">
      <Play v-if="!isPlaying" class="w-5 h-5 ml-0.5" />
      <Pause v-else class="w-5 h-5" />
    </button>

    <div class="flex flex-col gap-1 flex-1">
      <span class="text-sm font-unbounded">{{ title }}</span>
      <span class="text-sm text-white/70">{{ subtitle }}</span>
      <div class="relative h-1 bg-white/30 rounded cursor-pointer" @click="seek">
        <div class="h-full bg-white rounded transition-all"
             :style="{ width: `${progress}%` }" />
      </div>
    </div>

    <span class="text-sm text-white/70 tabular-nums select-none">{{ currentTime }} / {{ duration }}</span>

    <audio ref="audioRef" :src="props.src"
           preload="metadata"
           @timeupdate="onTimeUpdate"
           @loadedmetadata="onLoaded" />
  </div>
</template>