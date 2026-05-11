<script setup lang="ts">
import {Trash2, BookImage, Image, PackageOpen} from '@lucide/vue'
import {computed, onMounted, ref} from "vue";
import {useGalleriesStore} from "@stores/gallery.ts";

interface OrphanGallery {
  gallery: string;
  image: string;
  src: string;
}

const galleryStore = useGalleriesStore()
const selectedOrphans = ref<string[]>([])
const emit = defineEmits<{ requestDelete: [srcs: string[]] }>()

const orphansUrl = ref<string[]>([])
const orphans = ref<OrphanGallery[]>([])

// Fetch orphan audio files from store and transform them into structured data for UI
onMounted(async () => {
  await galleryStore.fetchOrphans()
      .then(() => {
        orphansUrl.value = galleryStore.orphans
        formatData()
      })
      .catch(error => console.error('Error fetching orphans:', error))
})

// Group orphan images by gallery
const groupedOrphans = computed(() => {
  return orphans.value.reduce((acc, orphan) => {
    if (!acc[orphan.gallery]) acc[orphan.gallery] = []
    acc[orphan.gallery].push(orphan)
    return acc
  }, {} as Record<string, OrphanGallery[]>)
})

// Toggle selection of all tracks
const toggleSelectAll = () => {
  if (selectedOrphans.value.length === orphans.value.length) {
    selectedOrphans.value = []
  } else {
    selectedOrphans.value = orphans.value.map(o => o.src)
  }
}

// Toggle selection of all tracks for a given album
const toggleSelectGallery = (galleryName: string) => {
  const albumSrcs = groupedOrphans.value[galleryName].map(o => o.src)

  const allSelected = albumSrcs.every(src => selectedOrphans.value.includes(src))

  if (allSelected) {
    selectedOrphans.value = selectedOrphans.value.filter(src => !albumSrcs.includes(src))
  } else {
    selectedOrphans.value = [...new Set([...selectedOrphans.value, ...albumSrcs])]
  }
}

// Toggle selection of a single image
const toggleSelectImage = (src: string) => {
  if (selectedOrphans.value.includes(src)) {
    selectedOrphans.value = selectedOrphans.value.filter(s => s !== src)
  } else {
    selectedOrphans.value = [...selectedOrphans.value, src]
  }
}

// Check if all images of gallery are currently selected
const isGallerySelected = (galleryName: string) => {
  const gallerySrcs = groupedOrphans.value[galleryName].map(o => o.src)
  return gallerySrcs.every(src => selectedOrphans.value.includes(src))
}

// Convert raw file paths into structured objects with human-readable labels
const formatData = () => {
  orphans.value = orphansUrl.value.map(url => {
    // Split the URL into gallery, image, and track slugs
    const [gallerySlug, imageSlug] = url.split('/')
    // Convert slug (e.g., "image_0001.webp") into "Image 0001" for readability
    const toLabel = (slug: string) => slug
        .replace(/\.[^.]+$/, '')     // remove extension (e.g., .webp)
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')

    return {
      gallery: toLabel(gallerySlug),
      image: toLabel(imageSlug),
      src: url
    } as OrphanGallery
  })
}
</script>

<template>
  <!-- Orphan audios -->
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="text-2xl font-unbounded font-semibold">Orphan galleries</h2>
        <p class="text-sm text-gray-500 mt-1">Files present on the server but not linked to any track.</p>
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
        <!-- Delete selected -->
        <button
            v-if="selectedOrphans.length > 0"
            @click="emit('requestDelete', selectedOrphans)"
            class="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-200 text-red-800 font-semibold border border-red-200 hover:bg-red-600 hover:text-white transition group">
          <Trash2 class="w-6 h-6"/>
          Delete selected
          <span class="w-6 h-6 flex items-center justify-center border rounded-full text-sm bg-red-100 group-hover:bg-red-700 transition">
            {{ selectedOrphans.length }}
          </span>
        </button>
      </div>

      <!-- Group by gallery -->
      <div v-for="(images, galleryName) in groupedOrphans" :key="galleryName"
           class="border border-gray-200 rounded-xl overflow-hidden">
        <!-- Gallery header -->
        <div @click="toggleSelectGallery(galleryName)"
             class="px-4 py-2 flex items-center gap-2 border-b border-gray-200 hover:bg-primary-600/30 cursor-pointer transition select-none"
             :class="isGallerySelected(galleryName) ? 'bg-primary-600/50' : 'bg-primary-200/30'">
          <BookImage class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transtion"
                 :class="isGallerySelected(galleryName) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
          <span :class="isGallerySelected(galleryName) ? 'font-semibold' : 'font-medium'">{{ galleryName }}</span>
        </div>

          <!-- Images -->
          <div v-for="orphan in images" :key="orphan.src"
               @click="toggleSelectImage(orphan.src)"
               class="flex items-center gap-3 px-8 py-2 hover:bg-orange-100 transition border-b border-gray-100 last:border-0 cursor-pointer select-none"
               :class="selectedOrphans.includes(orphan.src) ? 'bg-orange-200/80' : 'bg-orange-200/50'">
            <Image class="shrink-0 rounded-full p-1 w-8 h-8 border-blue-500 transition"
                    :class="selectedOrphans.includes(orphan.src) ? 'border-2 text-blue-500 bg-blue-100' : 'text-gray-400'"/>
            <span :class="selectedOrphans.includes(orphan.src) ? 'font-semibold' : 'font-medium'">{{
                orphan.image
              }}</span>
            <span class="text-xs text-gray-400 ml-auto font-mono">{{ orphan.src }}</span>
          </div>
        </div>
    </div>
  </div>
</template>

<style scoped>

</style>