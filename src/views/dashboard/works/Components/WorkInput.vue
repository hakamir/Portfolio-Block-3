<script setup lang="ts">
import {GripVertical, Upload} from "@lucide/vue"
import {onBeforeUnmount, onMounted, ref} from "vue";
import {type Track, useAudioStore} from "@stores";
import AudioPlayerMini from "@components/AudioPlayerMini.vue";

const props = defineProps<{
  type: 'artist' | 'album' | 'track'
  placeholder: string
  track?: Track
  src?: string
}>()

const apiUrl = import.meta.env.VITE_API_URL
const fileExists = ref(false)
const audioStore = useAudioStore()
const model = defineModel<string>({required: true})

const fileInputRef = ref<HTMLInputElement | null>(null)
const localSrc = ref<string | null>(null)

const handleUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !props.track) return
  audioStore.pendingUploads.set(props.track, file)
  localSrc.value = URL.createObjectURL(file)
}

onMounted(async () => {
  fileExists.value = await audioStore.checkAudioExists(props.src)
})

onBeforeUnmount(() => {
  if (localSrc.value) URL.revokeObjectURL(localSrc.value)
})

const labelClass = {
  artist: 'work-label-artist',
  album: 'work-label-album',
  track: 'work-label-track',
}

const inputClass = {
  artist: 'work-input-artist',
  album: 'work-input-album',
  track: 'work-input-track',
}

const labelText = {
  artist: 'Artist',
  album: 'Album',
  track: 'Track',
}
</script>

<template>
  <label :class="[labelClass[type], 'group']">
    <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
    {{ labelText[type] }}
  </label>

  <div v-if="type === 'track'">
    <!-- Fichier en attente d'upload (sélectionné localement) -->
    <AudioPlayerMini
        v-if="localSrc"
        :src="localSrc"
        :isLocal="true"
        className="work-upload-btn min-w-16 group flex items-center justify-center"
    />
    <!-- Fichier déjà présent sur le serveur -->
    <AudioPlayerMini
        v-else-if="fileExists"
        :src="`${apiUrl}/uploads/audio/${src}`"
        :isLocal="false"
        className="work-upload-btn min-w-16 group flex items-center justify-center"
    />
    <!-- Aucun fichier : bouton upload -->
    <button v-else @click="handleUpload"
            class="work-upload-btn group min-w-16 flex items-center justify-center">
      <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
    </button>

    <input ref="fileInputRef" type="file" accept=".mp3,audio/*" class="hidden" @change="handleFileChange"/>
  </div>
  <input
      type="text"
      :class="[inputClass[type], 'placeholder:text-gray-400 placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75']"
      :placeholder="placeholder"
      v-model="model"
  />
</template>