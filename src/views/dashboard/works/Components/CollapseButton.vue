<script setup lang="ts">
import { ListChevronsDownUp, ListChevronsUpDown } from "@lucide/vue"

const props = defineProps<{ collapsed: boolean, color?: string }>()
const emit = defineEmits<{ toggle: [] }>()
</script>

<template>
  <button @click="emit('toggle')" class="px-3 py-2 border-l border-y border-gray-300 rounded-l-full group" :class="props.color">
    <ListChevronsDownUp v-if="!props.collapsed" class="text-gray-400 group-hover:text-gray-500 group-hover:translate-x-1 transition"/>
    <ListChevronsUpDown v-else class="text-gray-400 group-hover:text-gray-500 group-hover:translate-x-1 transition"/>
  </button>
</template>