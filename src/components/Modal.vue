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
  closeOnBackdrop?: boolean
}>()

const emit = defineEmits<{ close: [] }>()

const buttonClass: Record<string, string> = {
  cancel: 'border border-gray-200 text-black hover:bg-black hover:text-white',
  confirm: 'bg-lime-600 text-white hover:bg-lime-500',
  delete: 'bg-red-500 text-white hover:bg-red-600',
  ok: 'bg-blue-600 text-white hover:bg-blue-500',
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
       @click.self="closeOnBackdrop !== false && emit('close')">
    <div class="bg-gray-100 rounded-2xl shadow-xl max-w-sm w-full mx-4 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center gap-3 px-6 py-4 border-b border-gray-300">
        <component v-if="icon" :is="icon" class="w-5 h-5 text-gray-500 shrink-0"/>
        <span class="font-semibold text-gray-800 grow">
          <slot name="header"/>
        </span>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition">
          <X class="w-6 h-6"/>
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-4">
        <slot/>
      </div>

      <!-- Footer -->
      <div v-if="buttons?.length" class="flex justify-end gap-2 px-6 py-4 border-t border-gray-300">
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