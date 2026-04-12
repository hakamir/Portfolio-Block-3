<script setup lang="ts">
import {ref, onMounted, watch, onBeforeUnmount, computed} from 'vue'
import {Upload} from '@lucide/vue'
import {useGalleriesStore, type Image} from '@stores/gallery.ts'
import DatePicker from "@components/DatePicker.vue";

const props = defineProps<{
  image: Image
  gallerySlug: string
}>()

const galleriesStore = useGalleriesStore()
const apiUrl = import.meta.env.VITE_API_URL

const fileInputRef = ref<HTMLInputElement | null>(null)
const localSrc = ref<string | null>(null)
const fileExists = ref(false)

const fullSrc = computed(() =>
    `${apiUrl}/uploads/gallery/${props.gallerySlug}/${props.image.src}`
)

const showPreview = ref(false)

onMounted(async () => {
  if (props.image.src) {
    fileExists.value = await galleriesStore.checkImageExists(fullSrc.value)
  }
})

watch(() => fullSrc.value, async (newSrc) => {
  if (!newSrc) return
  const url = new URL(newSrc)
  const segments = url.pathname.split('/').filter(Boolean)
  if (segments.length < 4 || segments.some(s => !s)) return
  fileExists.value = await galleriesStore.checkImageExists(newSrc)
}, {immediate: false})

const handleUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  galleriesStore.pendingUploads.set(props.image, file)
  localSrc.value = URL.createObjectURL(file)
  if (fileInputRef.value) fileInputRef.value.value = ''
}

onBeforeUnmount(() => {
  if (localSrc.value) URL.revokeObjectURL(localSrc.value)
})
</script>

<template>
  <div class="w-2 bg-yellow-200/30 border-x border-b border-gray-400/30 mx-4 mb-6 rounded-b-full"/>
  <div class="flex grow items-center">
    <div class="px-3 py-2 bg-orange-200/50 font-semibold rounded-bl-2xl border-l border-b border-gray-300">
      Location
    </div>
    <input
        class="bg-white px-3 py-2 border-l border-b border-gray-300 focus:outline-none placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75 font-semibold"
        v-model="image.location"/>
    <div class="px-3 py-2 bg-orange-200/50 font-semibold border-l border-b border-gray-300">Date</div>
    <DatePicker v-model="image.date.$date" />

    <button v-if="localSrc" @click="showPreview = true"
            class="px-1 border-b border-r border-gray-300 bg-gray-200/50 hover:bg-gray-300/50 transition">
      <img v-if="localSrc" :src="localSrc"
           class="w-10 h-10 object-cover rounded-lg border border-gray-300"/>
    </button>
    <button v-else-if="fileExists" @click="showPreview = true"
            class="px-1 border-b border-r border-gray-300 bg-gray-200/50 hover:bg-gray-300/50 transition">
      <img :src="fullSrc"
           class="w-10 h-10 object-cover rounded-lg border border-gray-300"/>
    </button>
    <button @click="handleUpload"
            class="px-3 py-2 border-b border-r border-gray-300 bg-gray-200/50 hover:bg-gray-300/50 transition rounded-br-2xl"
            :class="(localSrc || fileExists) ? 'opacity-60 hover:opacity-100' : ''">
      <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
    </button>
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showPreview"
             @click="showPreview = false"
             class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm cursor-pointer">
          <img :src="localSrc ?? fullSrc"
               class="max-w-[90vw] max-h-[90vh] object-contain rounded-2xl shadow-[0_0_20px_rgba(0,0,0,0.5)] cursor-pointer"
               @click="showPreview = false"
          />
        </div>
      </Transition>
    </Teleport>
    <input ref="fileInputRef" type="file" accept=".webp,.jpg,.jpeg,.png" class="hidden"
           @change="handleFileChange"/>
  </div>
</template>