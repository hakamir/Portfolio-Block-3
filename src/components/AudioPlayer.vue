<script setup lang="ts">
import {onBeforeUnmount, onMounted, ref} from 'vue'
import {Play, Pause} from '@lucide/vue'
import {useAudioPlayerStore} from "@stores";

const props = defineProps<{
  src: string
  title: string
  subtitle: string
}>()

const playerStore = useAudioPlayerStore()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const progress = ref(0) // Progress in percentage
const currentTime = ref('0:00')
const duration = ref('0:00')
const isDragging = ref(false)
const barRef = ref<HTMLDivElement | null>(null)

// Format time in mm:ss format
const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// Toggle play/pause
const togglePlay = () => {
  if (!audioRef.value) return
  if (isPlaying.value) {
    playerStore.pause(audioRef.value)
    isPlaying.value = false
  } else {
    playerStore.play(audioRef.value, {title: props.title, subtitle: props.subtitle, src: props.src})
    isPlaying.value = true
  }
}

const onPause = () => {
  isPlaying.value = false
}

onMounted(() => {
  audioRef.value?.addEventListener('pause', onPause)
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', stopDrag)
})
onBeforeUnmount(() => {
  audioRef.value?.removeEventListener('pause', onPause)
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', stopDrag)
})

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

const updateSeek = (clientX: number) => {
  const audio = playerStore.currentTrack
  if (!audio || !barRef.value) return
  const rect = barRef.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(clientX - rect.left, rect.width))
  audio.currentTime = (x / rect.width) * audio.duration
}

const startDrag = (event: MouseEvent | TouchEvent) => {
  isDragging.value = true
  const clientX = event instanceof TouchEvent ? event.touches[0].clientX : event.clientX
  updateSeek(clientX)
}

const onMouseMove = (event: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  const clientX = event instanceof TouchEvent ? event.touches[0].clientX : event.clientX
  updateSeek(clientX)
}

const stopDrag = () => {
  isDragging.value = false
}

const seek = (event: MouseEvent | TouchEvent) => {
  const audio = playerStore.currentTrack
  if (!audio || !barRef.value) return
  const clientX = event instanceof TouchEvent ? event.touches[0].clientX : event.clientX
  updateSeek(clientX)
}

</script>

<template>
  <div class="flex items-center gap-4">
    <button @click="togglePlay"
            class="w-12 h-12 rounded-full bg-white text-black flex items-center justify-center hover:bg-neutral-200 transition" aria-label="Play/Pause">
      <Play v-if="!isPlaying" class="w-5 h-5 ml-0.5"/>
      <Pause v-else class="w-5 h-5"/>
    </button>

    <div class="flex flex-col gap-1 flex-1">
      <span class="text-sm font-unbounded">{{ title }}</span>
      <span class="text-sm text-white/70">{{ subtitle }}</span>

      <div class="hidden sm:flex text-sm relative h-8 cursor-pointer group items-center" >
        <div ref="barRef" class="relative w-full h-1 bg-white/30 rounded-full"
             @mousedown="startDrag"
             @touchstart.prevent="startDrag"
             @mousemove="onMouseMove"
             @touchmove.prevent="onMouseMove"
             @mouseup="stopDrag"
             @touchend="stopDrag"
             @click="seek">
          <div class="h-full bg-white rounded-full"
               :style="{ width: `${progress}%` }"/>
          <div
              class="absolute top-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-100"
              :style="{
                 left: `${progress}%`,
                 transform: 'translate(-50%, -50%)'
               }"/>
        </div>
      </div>
    </div>

    <span class="hidden sm:inline text-sm text-white/70 tabular-nums select-none">{{ currentTime }} / {{ duration }}</span>

    <audio ref="audioRef" :src="props.src"
           preload="metadata"
           @timeupdate="onTimeUpdate"
           @loadedmetadata="onLoaded"/>
  </div>
</template>