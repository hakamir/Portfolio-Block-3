<script setup lang="ts">
import type {OrphanGallery} from '@stores'
import {Trash2, BookImage, Image, PackageOpen, RotateCcw} from '@lucide/vue'
import {computed, onMounted, ref} from "vue";
import {useOrphansStore} from "@stores";

const orphansStore = useOrphansStore()
const selectedOrphans = ref<string[]>([])
const emit = defineEmits<{
  requestDelete: [ids: string[]],
  requestRollback: [ids: string[]]
}>()

onMounted(async () => {
  await orphansStore.fetchOrphanGalleries()
})

const orphans = computed(() => orphansStore.orphanGalleries)

// Group orphan images by gallery_title
const groupedOrphans = computed(() => {
  return orphans.value.reduce((acc, orphan) => {
    if (!acc[orphan.gallery_title]) acc[orphan.gallery_title] = []
    acc[orphan.gallery_title].push(orphan)
    return acc
  }, {} as Record<string, OrphanGallery[]>)
})

const toggleSelectAll = () => {
  if (selectedOrphans.value.length === orphans.value.length) {
    selectedOrphans.value = []
  } else {
    selectedOrphans.value = orphans.value.map(o => o._id)
  }
}

const toggleSelectGallery = (galleryName: string) => {
  const galleryIds = groupedOrphans.value[galleryName].map(o => o._id)
  const allSelected = galleryIds.every(id => selectedOrphans.value.includes(id))
  if (allSelected) {
    selectedOrphans.value = selectedOrphans.value.filter(id => !galleryIds.includes(id))
  } else {
    selectedOrphans.value = [...new Set([...selectedOrphans.value, ...galleryIds])]
  }
}

const toggleSelectImage = (id: string) => {
  if (selectedOrphans.value.includes(id)) {
    selectedOrphans.value = selectedOrphans.value.filter(s => s !== id)
  } else {
    selectedOrphans.value = [...selectedOrphans.value, id]
  }
}

const isGallerySelected = (galleryName: string) => {
  const galleryIds = groupedOrphans.value[galleryName].map(o => o._id)
  return galleryIds.every(id => selectedOrphans.value.includes(id))
}

const canRollback = computed(() => selectedOrphans.value.length > 0)
</script>

<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="text-2xl font-unbounded font-semibold">Orphan galleries</h2>
        <p class="text-sm text-gray-500 mt-1">Files present on the server but not linked to any gallery.</p>
      </div>
    </div>

    <!-- No orphans -->
    <div v-if="orphans.length === 0"
         class="flex flex-col items-center justify-center py-8 gap-2">
      <PackageOpen class="w-10 h-10 text-gray-400"/>
      <span class="text-md text-gray-500 font-unbounded">No orphan galleries found...</span>
    </div>

    <!-- Orphans list -->
    <div v-else class="flex flex-col gap-2">

      <!-- Select all -->
      <div class="flex justify-between items-center mb-2">
        <label
            class="bg-gray-200 flex items-center gap-2 text-gray-700 cursor-pointer select-none border border-gray-200 rounded-xl px-4 py-2 has-[input:checked]:bg-blue-400 has-[input:checked]:text-white transition">
          <input type="checkbox"
                 :checked="selectedOrphans.length === orphans.length"
                 @change="toggleSelectAll"
                 class="hidden"/>
          Select all ({{ selectedOrphans.length }} / {{ orphans.length }})
        </label>
        <div class="flex gap-2 justify-between">
          <!-- Rollback selected -->
          <button
              v-if="canRollback"
              @click="emit('requestRollback', selectedOrphans)"
              class="flex items-center gap-2 px-4 py-2 rounded-xl bg-lime-200 text-lime-800 font-semibold border border-green-200 hover:bg-lime-600 hover:text-white transition group">
            <RotateCcw class="w-6 h-6"/>
            Restore selected
            <span
                class="w-6 h-6 flex items-center justify-center border rounded-full text-sm bg-green-100 group-hover:bg-lime-700 transition">
              {{ selectedOrphans.length }}
            </span>
          </button>
          <!-- Delete selected -->
          <button
              v-if="selectedOrphans.length > 0"
              @click="emit('requestDelete', selectedOrphans)"
              class="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-200 text-red-800 font-semibold border border-red-200 hover:bg-red-600 hover:text-white transition group">
            <Trash2 class="w-6 h-6"/>
            Delete selected
            <span
                class="w-6 h-6 flex items-center justify-center border rounded-full text-sm bg-red-100 group-hover:bg-red-700 transition">
              {{ selectedOrphans.length }}
            </span>
          </button>
        </div>
      </div>

      <!-- Group by gallery -->
      <div v-for="(images, galleryName) in groupedOrphans" :key="galleryName"
           class="border border-gray-200 rounded-xl overflow-hidden">
        <!-- Gallery header -->
        <div @click="toggleSelectGallery(galleryName)"
             class="px-4 py-2 flex items-center gap-2 border-b border-gray-200 hover:bg-primary-600/30 cursor-pointer transition select-none"
             :class="isGallerySelected(galleryName) ? 'bg-primary-600/50' : 'bg-primary-200/30'">
          <BookImage class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transition"
                     :class="isGallerySelected(galleryName) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
          <span :class="isGallerySelected(galleryName) ? 'font-semibold' : 'font-medium'">{{ galleryName }}</span>
        </div>

        <!-- Images -->
        <div v-for="orphan in images" :key="orphan._id"
             @click="toggleSelectImage(orphan._id)"
             class="flex items-center gap-3 px-8 py-2 hover:bg-orange-100 transition border-b border-gray-100 last:border-0 cursor-pointer select-none"
             :class="selectedOrphans.includes(orphan._id) ? 'bg-orange-200/80' : 'bg-orange-200/50'">
          <Image class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transition"
                 :class="selectedOrphans.includes(orphan._id) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
          <span :class="selectedOrphans.includes(orphan._id) ? 'font-semibold' : 'font-medium'">
            {{ orphan.image_title }}
          </span>
          <span class="text-xs text-gray-400 ml-auto font-mono">{{ orphan.src }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
