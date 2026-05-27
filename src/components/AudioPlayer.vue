<script setup lang="ts">
import {onBeforeUnmount, onMounted, ref} from 'vue'
import {Play, Pause, Tag} from '@lucide/vue'
import {useAudioPlayerStore} from "@stores"
import {useSearchStore} from "@stores/search"
import type {SearchEntry} from "@composables/useSearchIndex"

const props = defineProps<{
  src: string
  title: string
  subtitle: string
  tags: string[]
}>()

const playerStore = useAudioPlayerStore()
const searchStore = useSearchStore()

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

// Seek the audio to the position matching clientX within the progress bar
const updateSeek = (clientX: number) => {
  const audio = audioRef.value
  if (!audio || !barRef.value) return
  const rect = barRef.value.getBoundingClientRect()
  const x = Math.max(0, Math.min(clientX - rect.left, rect.width))
  audio.currentTime = (x / rect.width) * audio.duration
}

// Start a drag session and immediately seeks to the pointer position
const startDrag = (event: MouseEvent | TouchEvent) => {
  isDragging.value = true
  const clientX = event instanceof TouchEvent ? event.touches[0].clientX : event.clientX
  updateSeek(clientX)
}

// Continue seeking while dragging across the progress bar
const onMouseMove = (event: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return
  const clientX = event instanceof TouchEvent ? event.touches[0].clientX : event.clientX
  updateSeek(clientX)
}

// End the dragging - Triggered by @mouseup or @touchend events
const stopDrag = () => {
  isDragging.value = false
}

// Handle a simple click on the progress bar (no drag).
// Distinct from startDrag because @click fires after @mouseup: if both called updateSeek, a drag-release would seek twice
const seek = (event: MouseEvent | TouchEvent) => {
  const audio = audioRef.value
  if (!audio || !barRef.value) return
  const clientX = event instanceof TouchEvent ? event.touches[0].clientX : event.clientX
  updateSeek(clientX)
}

// Build a SearchEntry for a tag string, matching the shape produced by buildEntries() in useSearchIndex
// id format must stay in sync.
const tagEntry = (tag: string): SearchEntry => ({
  type: 'tag',
  id: `tag/${tag}`,
  name: tag,
  sub: null,
})

// Return true if the given tag is currently in the active filters
const isTagActive = (tag: string): boolean =>
    searchStore.activeFilters.some(f => f.id === `tag/${tag}`)

// Add or removes the tag filter depending on its current state
const toggleTag = (tag: string) => {
  if (isTagActive(tag)) {
    searchStore.removeFilter(`tag/${tag}`)
  } else {
    searchStore.addFilter(tagEntry(tag))
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-4 flex-1 min-w-0">
        <!-- Play Button -->
        <button @click="togglePlay"
                class="w-12 h-12 rounded-full bg-white text-black flex items-center justify-center hover:bg-neutral-200 transition shrink-0"
                aria-label="Play/Pause">
          <Play v-if="!isPlaying" class="w-5 h-5 ml-0.5"/>
          <Pause v-else class="w-5 h-5"/>
        </button>

        <!-- Titles (track / artist - album) -->
        <div class="flex flex-col gap-1 min-w-0">
          <span class="text-sm font-unbounded truncate">{{ title }}</span>
          <span class="text-sm text-white/70 truncate">{{ subtitle }}</span>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="tags.length > 0" class="flex items-center gap-1.5 flex-wrap shrink-0">
        <button
            v-for="tag in tags"
            :key="tag"
            :class="[
              'flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium transition select-none',
              'border backdrop-blur-sm',
              isTagActive(tag)
                ? 'bg-amber-500/30 text-amber-200 border-amber-400/50 hover:bg-amber-500/40'
                : 'bg-amber-500/10 text-amber-300 border-amber-500/20 hover:bg-amber-500/20'
            ]"
            @click="toggleTag(tag)"
            :aria-pressed="isTagActive(tag)"
            :aria-label="`Filter by tag: ${tag}`"
        >
          <Tag class="w-3 h-3"/>
          {{ tag }}
        </button>
      </div>

      <!-- Time -->
      <span class="hidden sm:inline text-sm text-white/70 tabular-nums select-none shrink-0">
        {{ currentTime }} / {{ duration }}
      </span>

      <!-- Audio file -->
      <audio ref="audioRef" :src="props.src"
             preload="metadata"
             @timeupdate="onTimeUpdate"
             @loadedmetadata="onLoaded"/>
    </div>

    <!-- Drag bar -->
    <div class="hidden sm:flex text-sm relative h-8 cursor-pointer group items-center"
         @mousedown="startDrag"
         @touchstart.prevent="startDrag"
         @mousemove="onMouseMove"
         @touchmove.prevent="onMouseMove"
         @mouseup="stopDrag"
         @touchend="stopDrag"
         @click="seek">
      <div ref="barRef" class="relative w-full h-1 bg-white/30 rounded-full">
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
</template>