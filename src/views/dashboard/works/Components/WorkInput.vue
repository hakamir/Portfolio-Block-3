<script setup lang="ts">
import {GripVertical} from "@lucide/vue"
import {computed} from "vue";
import {useGalleriesStore} from "@stores/gallery.ts";
import type {Gallery} from "@stores/gallery.ts";

const props = defineProps<{
  label: string
  labelColor?: string
  inputColor?: string
  placeholder?: string
  type?: string
  gallery?: Gallery
}>()

const store = useGalleriesStore()

const model = defineModel<string>({required: true})

const isInvalid = computed(() => {
  const empty = store.isSubmitted && !model.value?.trim()
  if (props.type === "gallery" && props.gallery) {
    return empty || store.isGalleryDuplicate(props.gallery)
  }
  return empty
})

</script>

<template>
  <label :class="['border-y border-gray-300 pr-4 py-2 font-semibold flex items-center',
                  'gap-2 cursor-grab select-none group',
                  labelColor]"
         class="drag-handle"
         aria-label="Drag to reorder images">
    <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
    {{ label }}
  </label>
  <input
      type="text"
      :class="['bg-white border border-gray-300 px-4 py-2 w-full font-semibold hover:bg-gray-50',
       'focus:outline-none transition-colors duration-300 placeholder:text-gray-400,',
        'placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75',
        isInvalid ? 'ring-2 ring-inset ring-red-500/70 transition' : '',
        inputColor]"
      :placeholder="placeholder"
      v-model="model"
      aria-label="Image title"
  />
</template>