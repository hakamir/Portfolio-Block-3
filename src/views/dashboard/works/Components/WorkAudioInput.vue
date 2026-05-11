<script setup lang="ts">
import {GripVertical, Upload} from "@lucide/vue"
import {computed, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {type Album, type Artist, type Track, useAudioStore} from "@stores";
import AudioPlayerMini from "@components/AudioPlayerMini.vue";

const props = defineProps<{
  type: 'artist' | 'album' | 'track'
  placeholder: string
  track?: Track
  album?: Album
  artist?: Artist
  src?: string
  debounceTime?: number
  submitted?: boolean
}>()
const fileExists = ref(false)
const audioStore = useAudioStore()

const uploadStatus = computed(() => props.track ? audioStore.uploadStatuses.get(props.track) : undefined)

const model = defineModel<string>({required: true})

const fileInputRef = ref<HTMLInputElement | null>(null)
const localSrc = ref<string | null>(null)

const handleUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !props.track) return
  audioStore.addPendingUpload(props.track, file)
  localSrc.value = URL.createObjectURL(file)
}

onMounted(async () => {
  if (props.type === 'track' && props.src) {
    fileExists.value = await audioStore.checkAudioExists(props.src, props.track)
  }
})

watch(() => props.track, async (newTrack) => {
  if (!newTrack || props.type !== 'track' || !props.src) return
  fileExists.value = await audioStore.checkAudioExists(props.src, newTrack)
})

onBeforeUnmount(() => {
  if (localSrc.value) URL.revokeObjectURL(localSrc.value)
})

let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(() => props.src, (newSrc) => {
  if (!newSrc) return
  if (debounceTimer) clearTimeout(debounceTimer)

  debounceTimer = setTimeout(async () => {
    fileExists.value = await audioStore.checkAudioExists(newSrc, props.track)
  }, props.debounceTime || 750)
})

const isInvalid = computed(() => {
  return audioStore.isSubmitted && !model.value?.trim()
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
  <label :class="[labelClass[type], 'group']" class="drag-handle">
    <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
    {{ labelText[type] }}
  </label>

  <div v-if="type === 'track'" class="flex items-center">
    <AudioPlayerMini
        v-if="localSrc || fileExists"
        :src="localSrc ?? src ?? ''"
        :title="track?.title"
        :subtitle="`${artist?.title} - ${album?.title}`"
        :status="uploadStatus"
        className="work-upload-btn min-w-16 group flex items-center justify-center"
    />

    <!-- Upload button : visible if no file OR to replace existing -->
    <button @click="handleUpload"
            class="work-upload-btn group min-w-16 flex items-center justify-center"
            :class="(localSrc || fileExists) ? 'opacity-60 hover:opacity-100' : ''">
      <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
    </button>

    <input
        ref="fileInputRef"
        type="file"
        accept=".mp3,.wma,.aac,.flac,.ogg,.wav,.aiff,.alac,.amr,.m4a"
        class="hidden"
        @change="handleFileChange"
    />
  </div>
  <input
      type="text"
      :class="[inputClass[type],
      isInvalid ? 'ring-2 ring-inset ring-red-500/70 transition' : '',
       'placeholder:text-gray-400 placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75']"
      :placeholder="placeholder"
      v-model="model"
  />
</template>