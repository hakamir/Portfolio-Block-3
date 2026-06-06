<script setup lang="ts">
import {ref, computed} from 'vue'
import {Search, X, Music, User, Disc, Tag} from '@lucide/vue'
import {useAudioStore} from '@stores/audio'
import {useSearchStore} from '@stores/search'
import {useSearchIndex} from '@composables/useSearchIndex'
import type {SearchResult} from '@composables/useSearchIndex'

const audioStore = useAudioStore()
const searchStore = useSearchStore()
const query = ref('')
const showResults = ref(false)
const {search} = useSearchIndex(() => audioStore.artists)
const results = computed(() => search(query.value))
const focusedIndex = ref(-1)

const onInput = () => {
  showResults.value = query.value.trim().length > 0
  focusedIndex.value = -1
}

const selectResult = (result: SearchResult) => {
  searchStore.addFilter(result)
  query.value = ''
  showResults.value = false
  focusedIndex.value = -1
}

// Slight delay when focus is lost
const onBlur = () => {
  setTimeout(() => {
    showResults.value = false
    focusedIndex.value = -1
  }, 150)
}

const typeIcons = {
  track: Music,
  artist: User,
  album: Disc,
  tag: Tag,
}

const typeBadgeClass: Record<string, string> = {
  track: 'bg-blue-500/15 text-blue-300',
  artist: 'bg-purple-500/15 text-purple-300',
  album: 'bg-teal-500/15 text-teal-300',
  tag: 'bg-amber-500/15 text-amber-300',
}

const typeLabels: Record<string, string> = {
  track: 'track',
  artist: 'artist',
  album: 'album',
  tag: 'tag',
}

const onKeydown = (e: KeyboardEvent) => {
  if (!showResults.value || results.value.length === 0) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedIndex.value = Math.min(focusedIndex.value + 1, results.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedIndex.value = Math.max(focusedIndex.value - 1, -1)
  } else if (e.key === 'Enter' && focusedIndex.value >= 0) {
    e.preventDefault()
    selectResult(results.value[focusedIndex.value])
  } else if (e.key === 'Escape') {
    showResults.value = false
    focusedIndex.value = -1
  }
}
</script>

<template>
  <div class="flex items-center gap-4 lg:ml-8 mb-8 flex-wrap">

    <!-- Input + dropdown -->
    <div class="relative">
      <div :class="['bg-gray-800/30 backdrop-blur-sm text-white',
                    'flex items-center gap-2 px-5 py-4',
                    'border border-gray-500/50 has-focus:border-gray-300/50 transition rounded-full',
                    'shadow-[0_0_15px_rgba(0,0,0,0.25)] has-focus:shadow-[0_0_20px_rgba(127,127,127,0.5)]']">
        <Search class="w-5 h-5 shrink-0 text-gray-400"/>
        <input
            v-model="query"
            type="text"
            placeholder="Search"
            class="bg-transparent outline-none text-lg text-white font-unbounded w-56"
            @input="onInput"
            @blur="onBlur"
            @focus="onInput"
            @keydown="onKeydown"
            aria-label="Search"
            role="searchbox"
        />
      </div>
      <!-- Dropdown -->
      <Transition name="dropdown">
        <div v-if="showResults && results.length > 0"
             class="absolute top-full mt-2 left-0 w-80 z-50 bg-gray-900/80 backdrop-blur-lg
                 border border-gray-600/50 rounded-2xl overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
          <div v-for="(result, index) in results"
               :key="result.id"
               class="w-full flex items-center justify-between gap-3 px-4 py-3
                   hover:bg-white/5 transition text-left border-b border-gray-700/40 last:border-0"
               :class="{ 'bg-white/5': focusedIndex === index }"
               @mousedown.prevent="selectResult(result)">
            <span class="min-w-0 flex flex-col">
              <span class="text-white font-medium truncate">{{ result.name }}</span>
              <span v-if="result.sub" class="text-gray-400 text-xs truncate mt-0.5">{{ result.sub }}</span>
            </span>
            <span :class="['flex items-center gap-1 px-2.5 py-1 rounded-full text-md font-medium shrink-0 select-none',
                           typeBadgeClass[result.type]]">
              <component :is="typeIcons[result.type]" class="w-3 h-3"/>
              {{ typeLabels[result.type] }}
            </span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Active filters -->
    <div v-if="searchStore.activeFilters.length > 0" class="flex items-center gap-2 flex-wrap">
      <span
          v-for="filter in searchStore.activeFilters"
          :key="filter.id"
          :class="['flex items-center gap-2 px-3 py-2 rounded-full backdrop-blur-sm',
                 'border border-gray-500/50 text-white/90 font-unbounded text-sm font-light select-none hover:scale-105 transition', typeBadgeClass[filter.type]]"
      >
        <component :is="typeIcons[filter.type]" class="w-6 h-6 text-gray-200"/>
        {{ filter.name }}
        <button
            class="text-gray-400 hover:text-white transition ml-0.5"
            @click="searchStore.removeFilter(filter.id)"
        >
          <X class="w-8 h-8 -m-1 p-1 hover:bg-gray-400/20 border border-gray-300/0 hover:border-gray-300 transition rounded-full"/>
        </button>
      </span>
    </div>

  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>