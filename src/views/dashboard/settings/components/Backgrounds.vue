<script setup lang="ts">
import {ref} from 'vue'
import {Pencil} from '@lucide/vue'
import BackgroundEditModal from "@views/dashboard/settings/components/BackgroundEditModal.vue";


export interface Background {
  key: string
  label: string
  src: string
  destination: string
  srcFull: string
}

const apiUrl = import.meta.env.VITE_API_URL + '/api'

const backgrounds: Background[] = [
  {
    key: 'hero',
    label: 'Hero',
    src: `${apiUrl}/upload/background/hero/hero-512.webp`,
    destination: 'hero',
    srcFull: `${apiUrl}/upload/background/hero/hero-2048.webp`,
  },
  {
    key: 'biography',
    label: 'Biography',
    src: `${apiUrl}/upload/biography/biography-1-512.webp`,
    destination: 'biography',
    srcFull: `${apiUrl}/upload/biography/biography-1-2048.webp`,
  },
  {
    key: 'portfolio',
    label: 'Portfolio',
    src: `${apiUrl}/upload/background/portfolio/portfolio-512.webp`,
    destination: 'portfolio',
    srcFull: `${apiUrl}/upload/background/portfolio/portfolio-2048.webp`,
  },
]

const selectedBackground = ref<Background | null>(null)

function openModal(bg: Background): void {
  selectedBackground.value = bg
}
</script>


<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="text-2xl font-unbounded font-semibold">Backgrounds</h2>
        <p class="text-sm text-gray-500 mt-1">Manage the background images for each section of the site.</p>
      </div>
    </div>

    <!-- Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
          v-for="bg in backgrounds"
          :key="bg.key"
          @click="openModal(bg)"
          class="group relative rounded-xl overflow-hidden border border-gray-200 cursor-pointer aspect-square bg-gray-200 transition hover:border-gray-400 hover:shadow-md"
      >
        <!-- Image -->
        <img
            :src="bg.src"
            :alt="bg.label"
            class="w-full h-full object-cover transition duration-300 group-hover:scale-105"
        />

        <!-- Overlay -->
        <div
            class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition duration-300 flex items-center justify-center">
          <div class="opacity-0 group-hover:opacity-100 transition duration-300 flex flex-col items-center gap-2">
            <Pencil class="w-7 h-7 text-white drop-shadow"/>
            <span class="text-white text-sm font-semibold font-unbounded drop-shadow">Modify</span>
          </div>
        </div>

        <!-- Label badge -->
        <div class="absolute bottom-0 left-0 right-0 px-3 py-2 bg-linear-to-t from-black/60 to-transparent">
          <span class="text-white text-sm font-unbounded font-medium capitalize">{{ bg.label }}</span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <BackgroundEditModal
        v-if="selectedBackground"
        :background="selectedBackground"
        @close="selectedBackground = null"
    />
  </div>
</template>