<script setup lang="ts">
import { GripVertical, Upload } from "@lucide/vue"

defineProps<{
  type: 'artist' | 'album' | 'track'
  placeholder: string
}>()

const model = defineModel<string>({ required: true })

const emit = defineEmits<{ upload: [] }>()

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

  <button v-if="type === 'track'" @click="emit('upload')" class="work-upload-btn group">
    <Upload class="text-gray-600 group-hover:text-gray-800 group-hover:translate-x-1 transition"/>
  </button>

  <input
    type="text"
    :class="[inputClass[type], 'placeholder:text-gray-400 placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75']"
    :placeholder="placeholder"
    v-model="model"
  />
</template>