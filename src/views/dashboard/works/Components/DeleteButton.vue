<script setup lang="ts">
import {Trash2} from "@lucide/vue";
defineProps({customClass: String})

const emit = defineEmits(['delete'])
</script>

<template>
  <button @click="emit('delete')"
          :class="customClass"
          class="bg-gray-200/50 border-y border-r border-gray-300 px-4 py-2 font-semibold flex items-center gap-1 cursor-pointer select-none transition-transform duration-300 group">
    <Trash2 class="text-red-700/60 group-hover:text-red-700 group-hover:scale-105 transition"/>
  </button>
</template>

<style scoped>

</style>