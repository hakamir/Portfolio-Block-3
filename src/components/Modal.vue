<script setup lang="ts">
import {X} from '@lucide/vue'

interface ModalButton {
  label: string
  type: 'cancel' | 'confirm' | 'delete' | 'ok'
  action: () => void
}

defineProps<{
  icon?: object
  buttons?: ModalButton[]
}>()

const emit = defineEmits<{ close: [] }>()

const buttonClass: Record<string, string> = {
  cancel: 'border border-gray-200 text-white hover:bg-gray-100 hover:text-gray-900',
  confirm: 'bg-lime-500 text-white hover:bg-lime-600',
  delete: 'bg-red-500 text-white hover:bg-red-600',
  ok: 'bg-blue-500 text-white hover:bg-blue-600',
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
       @click.self="emit('close')">
    <div class="bg-gray-800 rounded-2xl shadow-xl max-w-sm w-full mx-4 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center gap-3 px-6 py-4 border-b border-gray-700">
        <component v-if="icon" :is="icon" class="w-5 h-5 text-gray-500 shrink-0"/>
        <span class="font-semibold text-gray-200 grow">
          <slot name="header"/>
        </span>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition">
          <X class="w-4 h-4"/>
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-4 text-sm text-gray-400">
        <slot/>
      </div>

      <!-- Footer -->
      <div v-if="buttons?.length" class="flex justify-end gap-2 px-6 py-4 border-t border-gray-700">
        <button
            v-for="btn in buttons"
            :key="btn.label"
            @click="btn.action"
            :class="buttonClass[btn.type]"
            class="px-4 py-2 rounded-xl text-sm font-medium transition">
          {{ btn.label }}
        </button>
      </div>

    </div>
  </div>
</template>