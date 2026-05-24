<script setup lang="ts">
import {GripVertical, Upload} from "@lucide/vue"
import {computed, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {type Album, type Artist, type Track, useAudioStore} from "@stores";
import AudioPlayerMini from "@components/AudioPlayerMini.vue";
import TagSelector from "@views/dashboard/works/Components/TagSelector.vue";
import DeleteButton from "@views/dashboard/works/Components/DeleteButton.vue";

const props = defineProps<{
  type: 'artist' | 'album' | 'track'
  placeholder: string
  track?: Track
  album?: Album
  artist?: Artist
  src?: string
  debounceTime?: number
  submitted?: boolean
  index?: number
  isMobile?: boolean
}>()
const emit = defineEmits(['TagSelectorToggled', 'deleteTrack'])
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
  const empty = audioStore.isSubmitted && !model.value?.trim()

  if (props.type === 'artist' && props.artist) {
    return empty || audioStore.isArtistDuplicate(props.artist)
  }
  if (props.type === 'album' && props.album && props.artist) {
    return empty || audioStore.isAlbumDuplicate(props.album, props.artist)
  }
  if (props.type === 'track' && props.track && props.album) {
    return empty || audioStore.isTrackDuplicate(props.track, props.album)
  }

  return empty
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
  <!-- MOBILE -->
  <template v-if="isMobile && type === 'track'">
    <div class="flex">
      <label class="drag-handle flex items-center border-b border-r border-gray-300 px-2" aria-label="Reorder track">
        <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
      </label>
      <input
          type="text"
          :class="[inputClass[type],
        isInvalid ? 'ring-2 ring-inset ring-red-500/70 transition' : '',
         'placeholder:text-gray-400 placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75 py-3!']"
          :placeholder="placeholder"
          v-model="model"
          aria-label="title input"
      />
    </div>
    <div class="flex items-center col-span-full">
      <AudioPlayerMini
          v-if="localSrc || fileExists"
          :src="localSrc ?? src ?? ''"
          :title="track?.title"
          :subtitle="`${artist?.title} - ${album?.title}`"
          :status="uploadStatus"
          :isMobile="isMobile"
          className="work-upload-btn w-full group flex items-center justify-center"
      />
      <button @click="handleUpload"
              class="work-upload-btn group w-16 flex items-center justify-center"
              :class="!(localSrc || fileExists) ? 'w-full' : ''"
              aria-label="Upload audio">
        <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
      </button>
      <input
          ref="fileInputRef"
          type="file"
          accept=".mp3,.wma,.aac,.flac,.ogg,.wav,.aiff,.alac,.amr,.m4a"
          class="hidden"
          @change="handleFileChange"
          aria-label="Upload audio input"
          aria-hidden="true"
      />
      <TagSelector v-if="track" v-model="track.tags" @toggle="emit('TagSelectorToggled', track)" aria-label="Edit tags"/>
      <DeleteButton v-if="album && track" @delete="emit('deleteTrack', album, track)" assignedFor="track"
                    aria-label="Delete track"/>
    </div>
  </template>

  <!-- DESKTOP -->
  <template v-else>
    <label :class="[labelClass[type], 'group']" class="drag-handle" aria-label="Drag to reorder">
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
              :class="(localSrc || fileExists) ? 'opacity-60 hover:opacity-100' : ''" aria-label="Upload audio">
        <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
      </button>

      <input
          ref="fileInputRef"
          type="file"
          accept=".mp3,.wma,.aac,.flac,.ogg,.wav,.aiff,.alac,.amr,.m4a"
          class="hidden"
          @change="handleFileChange"
          aria-label="Upload audio input"
          aria-hidden="true"
      />
    </div>
    <!-- Input field -->
    <input
        type="text"
        :class="[inputClass[type],
        isInvalid ? 'ring-2 ring-inset ring-red-500/70 transition' : '',
         'placeholder:text-gray-400 placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75']"
        :placeholder="placeholder"
        v-model="model"
        aria-label="title input"
    />
    <!-- Tag selector -->
    <TagSelector v-if="track && type === 'track'" v-model="track.tags" @toggle="emit('TagSelectorToggled', track)"
                 aria-label="Edit tags"/>
    <!-- Delete track button -->
    <DeleteButton v-if="album && track && type === 'track'" @delete="emit('deleteTrack', album, track)"
                  assignedFor="track"
                  :customClass="index === album.tracks.length - 1 ? 'rounded-br-2xl' : ''" aria-label="Delete track"/>
  </template>
</template>