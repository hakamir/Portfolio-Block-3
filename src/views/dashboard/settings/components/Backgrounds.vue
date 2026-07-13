<script setup lang="ts">
import {onMounted, ref} from 'vue'
import {Pencil} from '@lucide/vue'
import BackgroundEditModal from "@views/dashboard/settings/components/BackgroundEditModal.vue";
import {useBackgroundStore} from "@stores/background.ts";
import backgroundApi from "@api/background.ts"
import {instance} from "@api/axios.ts";



export interface Background {
  key: string
  label: string
  src: string
  destination: string
  srcFull: string
}

const apiUrl = import.meta.env.VITE_API_URL + '/api'

const backgroundStore = useBackgroundStore()
const selectedBackground = ref<Background | null>(null)
const backgrounds = ref<Background[]>([])
const loading = ref(false)

const fetchOwnedBackgrounds = async () => {
    loading.value = true
    try {
        const res = await instance.get(backgroundApi.getOwnedBackgrounds)
        const data = res.data
        backgrounds.value = [
            {
                key: 'hero',
                label: 'Hero',
                src: `${apiUrl}${data.hero.sm}`,
                srcFull: `${apiUrl}${data.hero.lg}`,
                destination: 'hero',
            },
            {
                key: 'biography',
                label: 'Biography',
                src: `${apiUrl}${data.biography.sm}`,
                srcFull: `${apiUrl}${data.biography.lg}`,
                destination: 'biography',
            },
            {
                key: 'portfolio',
                label: 'Portfolio',
                src: `${apiUrl}${data.portfolio.sm}`,
                srcFull: `${apiUrl}${data.portfolio.lg}`,
                destination: 'portfolio',
            },
        ]
    } catch (e) {
        console.error('Failed to fetch backgrounds', e)
    } finally {
        loading.value = false
    }
}

const openModal = (bg: Background): void => {
  selectedBackground.value = bg
}

const onSave = async () => {
    await fetchOwnedBackgrounds()
    await backgroundStore.fetchBackground()
}

onMounted(fetchOwnedBackgrounds)
</script>


<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="text-2xl font-unbounded font-semibold">Backgrounds</h2>
        <p class="text-sm text-gray-500 mt-1">Manage the background images for each section of the site.</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-8">
      <span class="text-gray-400">Loading...</span>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
          v-for="bg in backgrounds"
          :key="bg.key"
          @click="openModal(bg)"
          class="group relative rounded-xl overflow-hidden border border-gray-200 cursor-pointer aspect-square bg-gray-200 transition hover:border-gray-400 hover:shadow-md"
      >
        <img
            :src="bg.src"
            :alt="bg.label"
            class="w-full h-full object-cover transition duration-300 group-hover:scale-105"
        />
        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition duration-300 flex items-center justify-center">
          <div class="opacity-0 group-hover:opacity-100 transition duration-300 flex flex-col items-center gap-2">
            <Pencil class="w-7 h-7 text-white drop-shadow"/>
            <span class="text-white text-sm font-semibold font-unbounded drop-shadow">Modify</span>
          </div>
        </div>
        <div class="absolute bottom-0 left-0 right-0 px-3 py-2 bg-linear-to-t from-black/60 to-transparent">
          <span class="text-white text-sm font-unbounded font-medium capitalize">{{ bg.label }}</span>
        </div>
      </div>
    </div>

    <BackgroundEditModal
        v-if="selectedBackground"
        :background="selectedBackground"
        @close="selectedBackground = null"
        @save="onSave"
    />
  </div>
</template>