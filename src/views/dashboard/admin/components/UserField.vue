<script setup lang="ts">
import {ref} from 'vue'
import {Check, Copy} from '@lucide/vue'

defineProps<{
  label: string
  value: string
  clipboard?: boolean
}>()

const copied = ref(false)

const copy = async (text: string) => {
  await navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1500)
}
</script>

<template>
  <div class="contents">
    <span
        class="font-unbounded bg-gray-100 border border-gray-300 px-5 py-2.5 rounded-l-full text-sm font-medium select-none whitespace-nowrap flex items-center justify-end">
      {{ label }}
    </span>
    <div type="button"
            @click="clipboard ? copy(value): null"
            :class="clipboard ? 'cursor-pointer hover:bg-gray-50 ' : ''"
            class="flex items-center justify-between gap-3 border-y border-r border-gray-300 bg-white px-5 py-2.5 rounded-r-full text-sm text-gray-700 transition group w-full min-w-0 text-left"
    >
      <span class="truncate">{{ value }}</span>
      <span v-if="clipboard" class="shrink-0">
        <Check v-if="copied" class="w-3.5 h-3.5 text-lime-600"/>
        <Copy v-else class="w-3.5 h-3.5 text-gray-300 group-hover:text-gray-500 transition"/>
      </span>
    </div>
  </div>
</template>
