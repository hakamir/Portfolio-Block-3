<script setup lang="ts">
import {GripVertical, Upload} from "@lucide/vue"
import {onMounted, ref} from "vue";
import {useAudioStore} from "@stores";
import AudioPlayerMini from "@components/AudioPlayerMini.vue";

const props = defineProps<{
  type: 'artist' | 'album' | 'track'
  placeholder: string
  src?: string
}>()

const apiUrl = import.meta.env.VITE_API_URL
const fileExists = ref(false)
const audioStore = useAudioStore()
const model = defineModel<string>({required: true})
const emit = defineEmits<{ upload: [src: string | undefined] }>()

onMounted(async () => {
  fileExists.value = await audioStore.checkAudioExists(props.src)
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

  <div v-if="type==='track'">
    <button v-if="!fileExists" @click="emit('upload', src)"
            class="work-upload-btn group min-w-16 flex items-center justify-center">
      <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
    </button>
      <AudioPlayerMini v-else className="work-upload-btn min-w-16 group flex items-center justify-center" :src="`${apiUrl}/uploads/audio/${src}`"/>
  </div>
  <input
      type="text"
      :class="[inputClass[type], 'placeholder:text-gray-400 placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75']"
      :placeholder="placeholder"
      v-model="model"
  />
</template>