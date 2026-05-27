<script setup lang="ts">
import {ref, watch, onBeforeUnmount, onMounted} from 'vue'
import {Play, Pause, Volume1, Volume2, VolumeX} from '@lucide/vue'
import {useAudioPlayerStore} from '@stores'

const playerStore = useAudioPlayerStore()

const progress = ref(0)
const currentTime = ref('0:00')
const duration = ref('0:00')
const isDragging = ref(false)
const barRef = ref<HTMLDivElement | null>(null)

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

const syncFromAudio = () => {
  const audio = playerStore.currentTrack
  if (!audio || isNaN(audio.duration)) return
  progress.value = (audio.currentTime / audio.duration) * 100
  currentTime.value = formatTime(audio.currentTime)
  duration.value = formatTime(audio.duration)
}

const onTimeUpdate = () => syncFromAudio()
const onLoaded = () => syncFromAudio()

watch(() => playerStore.currentTrack, (newTrack, oldTrack) => {
  if (oldTrack) {
    oldTrack.removeEventListener('timeupdate', onTimeUpdate)
    oldTrack.removeEventListener('loadedmetadata', onLoaded)
  }
  if (newTrack) {
    newTrack.addEventListener('timeupdate', onTimeUpdate)
    newTrack.addEventListener('loadedmetadata', onLoaded)
    syncFromAudio()
  } else {
    progress.value = 0
    currentTime.value = '0:00'
    duration.value = '0:00'
  }
})

onMounted(() => {
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', stopDrag)
})

onBeforeUnmount(() => {
  const audio = playerStore.currentTrack
  if (audio) {
    audio.removeEventListener('timeupdate', onTimeUpdate)
    audio.removeEventListener('loadedmetadata', onLoaded)
  }
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', stopDrag)
})

const togglePlay = () => {
  const audio = playerStore.currentTrack
  if (!audio || !playerStore.currentMeta) return
  if (playerStore.isPlaying) {
    playerStore.pause(audio)
  } else {
    playerStore.play(audio, playerStore.currentMeta)
  }
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

// Volume control
const volume = ref(50)   // 0–100
const isMuted = ref(false)

const applyVolume = () => {
  const audio = playerStore.currentTrack
  if (!audio) return
  audio.volume = isMuted.value ? 0 : volume.value / 100
}

watch(volume, applyVolume)

watch(() => playerStore.currentTrack, (newTrack) => {
  if (newTrack) newTrack.volume = isMuted.value ? 0 : volume.value / 100
})

const toggleMute = () => {
  isMuted.value = !isMuted.value
  applyVolume()
}
</script>

<template>
  <Transition name="sticky-player">
    <div v-if="playerStore.isPlaying"
         class="fixed z-50 bottom-0 left-0 right-0 overflow-hidden
              lg:translate-y-10 lg:hover:hover:translate-y-0 group/container transition duration-500 border-t border-white/10">
      <!-- Progressive white mask -->
      <div class="absolute inset-0 -z-10 h-full w-full bg-amber-200/30 blur-3xl" :style="{ width: `${progress}%` }"/>
      <!-- Gradient background mask -->
      <div class="absolute inset-0 z-0 bg-linear-0 from-black/90 via-black/80 to-black/60
              lg:from-black/60 lg:via-black/40 lg:to-black/20
              lg:group-hover/container:from-black/90 lg:group-hover/container:via-black/80 lg:group-hover/container:to-black/60 backdrop-blur-xl transition duration-500"/>

      <!-- Content -->
      <div class="relative flex items-center gap-1 lg:gap-4 container mx-auto px-6 py-3 z-20">
        <button @click="togglePlay"
                class="w-10 h-10 lg:w-12 lg:h-12 rounded-full bg-white text-black flex items-center justify-center hover:bg-neutral-200 shrink-0 lg:opacity-0 lg:group-hover/container:opacity-100 transition duration-300 group/button">
          <Play v-if="!playerStore.isPlaying" class="w-5 h-5 ml-0.5 group-hover/button:scale-105"/>
          <Pause v-else class="w-5 h-5"/>
        </button>

        <div class="flex flex-col gap-1 flex-1 min-w-0">
          <span
              class="text-white text-md lg:text-2xl font-unbounded truncate lg:p-2 lg:ml-2 text-shadow-[0_0_10px_rgba(0,0,0,1)]">{{
              playerStore.currentMeta?.title
            }}</span>
          <span
              class="text-white text-sm lg:font-thin lg:font-unbounded truncate lg:py-1 px-2 text-shadow-[0_0_5px_rgba(0,0,0,1)]">{{
              playerStore.currentMeta?.subtitle
            }}</span>

        </div>

        <span class="text-sm text-white/80 tabular-nums select-none shrink-0 text-shadow-[0_0_10px_rgba(0,0,0,1)]">
          {{ currentTime }} / {{ duration }}
        </span>

        <div class="hidden sm:flex items-center gap-2 shrink-0">
          <button @click="toggleMute" class="text-white/70 hover:text-white transition">
            <VolumeX v-if="isMuted || volume === 0" class="w-5 h-5"/>
            <Volume1 v-else-if="volume < 50" class="w-5 h-5"/>
            <Volume2 v-else class="w-5 h-5"/>
          </button>
          <input
              type="range"
              min="0" max="100"
              v-model.number="volume"
              class="volume-slider w-24 cursor-pointer"
              :style="{ '--fill': `${isMuted ? 0 : volume}%` }"
          />
        </div>
      </div>
      <div class="relative h-8 group flex items-center justify-center">
        <div ref="barRef" class="relative w-full mt-2 lg:w-2/3 h-1 bg-white/30 rounded-full cursor-pointer"
             @mousedown="startDrag"
             @touchstart.prevent="startDrag"
             @mousemove="onMouseMove"
             @touchmove.prevent="onMouseMove"
             @mouseup="stopDrag"
             @touchend="stopDrag"
             @click="seek">
          <div class="h-full bg-white rounded-full" :style="{ width: `${progress}%` }"/>
          <div
              class="absolute top-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-100"
              :style="{ left: `${progress}%`, transform: 'translate(-50%, -50%)' }"/>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.sticky-player-enter-active,
.sticky-player-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.sticky-player-enter-from,
.sticky-player-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

/* Volume slider */
.volume-slider {
  appearance: none;
  height: 4px;
  border-radius: 9999px;
  background: linear-gradient(
      to right,
      white var(--fill, 100%),
      rgba(255, 255, 255, 0.3) var(--fill, 100%)
  );
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  transition: transform 0.1s ease;
}

.volume-slider:hover::-webkit-slider-thumb {
  transform: scale(1.2);
}

.volume-slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  border: none;
  border-radius: 50%;
  background: white;
  cursor: pointer;
}

.volume-slider::-moz-range-track {
  height: 4px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.3);
}

.volume-slider::-moz-range-progress {
  height: 4px;
  border-radius: 9999px;
  background: white;
}
</style>
