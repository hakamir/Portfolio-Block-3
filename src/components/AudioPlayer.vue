<script setup lang="ts">
import {onBeforeUnmount, onMounted, ref, computed} from 'vue'
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

const dropdownOpen = ref(false)
const rootRef = ref<HTMLDivElement | null>(null)
const containerWidth = ref(0)
const visibleTags = computed(() => props.tags.slice(0, maxVisible.value)) // Shown tags
const hiddenTags = computed(() => props.tags.slice(maxVisible.value)) // Tags in the dropdown

let ro: ResizeObserver | null = null

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
  document.addEventListener('click', closeDropdown)
  if (rootRef.value) {
    // Check container size changes, store the new width,
    // observe rootRef then immediately init the width before observer triggers an event
    ro = new ResizeObserver(([entry]) => {
      containerWidth.value = entry.contentRect.width
    })
    ro.observe(rootRef.value)
    containerWidth.value = rootRef.value.getBoundingClientRect().width
  }
})
onBeforeUnmount(() => {
  audioRef.value?.removeEventListener('pause', onPause)
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('click', closeDropdown)
  ro?.disconnect()
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

// Number of tags shown directly, calculated on the width of the container
const maxVisible = computed(() => {
  if (containerWidth.value < 300) return 0
  if (containerWidth.value < 400) return 1
  if (containerWidth.value < 500) return 2
  if (containerWidth.value < 800) return 3
  if (containerWidth.value < 900) return 4
  if (containerWidth.value < 1000) return 5
  return props.tags.length // All visible (no dropdown)
})

const toggleDropdown = (e: MouseEvent) => {
  e.stopPropagation()
  dropdownOpen.value = !dropdownOpen.value
}

const closeDropdown = () => {
  dropdownOpen.value = false
}
</script>

<template>
  <div class="flex flex-col gap-2" ref="rootRef">
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
            v-for="tag in visibleTags"
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

        <!-- Dropdown (+n button) -->
        <div v-if="hiddenTags.length > 0" class="relative">
          <button
              @click="toggleDropdown"
              class="flex items-center justify-center px-2.5 py-1 rounded-full text-xs font-semibold transition select-none border border-white/15 bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/90"
              :aria-expanded="dropdownOpen"
              aria-haspopup="true"
          >
            +{{ hiddenTags.length }}
          </button>

          <Transition
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-1"
          >
            <div v-if="dropdownOpen"
                 @click.stop
                 class="absolute right-0 top-full mt-1.5 flex flex-col gap-1 p-1.5 rounded-xl border border-white/10 bg-neutral-900 shadow-2xl z-50 min-w-35">
              <button
                  v-for="tag in hiddenTags"
                  :key="tag"
                  :class="[
                    'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition select-none w-full text-left',
                    isTagActive(tag)
                      ? 'bg-amber-500/30 text-amber-200 hover:bg-amber-500/40'
                      : 'text-amber-300 hover:bg-amber-500/10'
                  ]"
                  @click="toggleTag(tag)"
                  :aria-pressed="isTagActive(tag)"
              >
                <Tag class="w-3 h-3 shrink-0"/>
                {{ tag }}
              </button>
            </div>
          </Transition>
        </div>
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