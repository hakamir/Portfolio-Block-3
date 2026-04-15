<script setup lang="ts">
import {GripVertical} from "@lucide/vue"

defineProps<{
  label: string
  labelColor?: string
  inputColor?: string
  placeholder?: string
}>()

const model = defineModel<string>({required: true})

</script>

<template>
  <label :class="['border-y border-gray-300 pr-4 py-2 font-semibold flex items-center',
                  'gap-2 cursor-grab select-none group',
                  labelColor]"

         class="drag-handle">
    <GripVertical class="text-gray-400 group-hover:text-gray-500 transition"/>
    {{ label }}
  </label>
  <input
      type="text"
      :class="['bg-white border border-gray-300 px-4 py-2 w-full font-semibold hover:bg-gray-50',
       'focus:outline-none transition-colors duration-300 placeholder:text-gray-400,',
        'placeholder:text-sm placeholder:font-light placeholder:italic placeholder:opacity-75',
        inputColor]"
      :placeholder="placeholder"
      v-model="model"
  />
</template>