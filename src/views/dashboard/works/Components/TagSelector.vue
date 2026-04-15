<script setup lang="ts">
import {Tag} from "@lucide/vue"

const model = defineModel<string[]>({required: true})

const emit = defineEmits(['toggle'])

</script>

<template>
  <button @click="emit('toggle')"
          class="border-b bg-gray-200/50 border-r border-gray-300 px-4 py-2 font-semibold flex items-center gap-1 cursor-pointer select-none transition-transform duration-300 group relative active:bg-gray-200">
    <Tag
        class="text-blue-600/80 group-hover:text-blue-700 group-hover:scale-105 group-hover:fill-blue-200 transition"/>
    <span
        class="w-4 h-4 absolute top-0.5 right-0.5 text-[10px] bg-blue-700 group-hover:bg-white text-white group-hover:text-blue-800 border border-gray-500 rounded-full flex items-center justify-center group-hover:scale-125 transition">
        <span v-if="model">
        {{ model.length }}
          </span>
        <span v-else>
          0
        </span>
      </span>
  </button>
</template>

<style scoped>

</style>