<script setup lang="ts">
import {watch} from 'vue'
import {useMessagesStore} from '@stores/messages'
import {storeToRefs} from 'pinia'
import {Reply} from "@lucide/vue";

const props = defineProps<{ selectedIds: string[] }>()
const emit = defineEmits<{ 'update:selectedIds': [value: string[]] }>()

const store = useMessagesStore()
const {filteredMessages, fetchStatus} = storeToRefs(store)

const toggleSelect = (id: string) => {
  const set = new Set(props.selectedIds)
  if (set.has(id)) set.delete(id)
  else set.add(id)
  emit('update:selectedIds', [...set])
}

watch(filteredMessages, () => {
  emit('update:selectedIds', [])
})

const format_date = (input: Date | string) => {
  const date = new Date(input)
  const now = Date.now()
  const diff = (now - date.getTime()) / 1000
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`
  if (diff < 86400) return date.toLocaleTimeString()

  const nowDate = new Date()

  if (nowDate.getFullYear() === date.getFullYear()) {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric'
    }).format(date)
  }

  return date.toLocaleDateString()
}
</script>

<template>
  <div class="w-full border border-neutral-200 rounded-2xl overflow-hidden">
    <div>
      <!-- Loading -->
      <div v-if="fetchStatus === 'loading'" class="border-b border-neutral-200">
        <div class="text-center">
          <p class="flex justify-center m-4">Chargement...</p>
        </div>
      </div>
      <!-- Error -->
      <div v-else-if="fetchStatus === 'error'" class="border-b border-neutral-200">
        <div class="text-center text-red-500">
          An error occurred while loading messages.
        </div>
      </div>
      <!-- Empty -->
      <div v-else-if="filteredMessages.length === 0" class="border-b border-neutral-200">
        <div class="text-center">No messages found.</div>
      </div>
      <!-- Messages -->
      <template v-else v-for="message in filteredMessages" :key="message._id">
        <div :class="!message.read ? 'font-bold bg-blue-50': 'bg-white'"
             class="cursor-pointer border-b border-neutral-200 flex justify-between hover:bg-gray-50">
          <div class="flex">
            <div class="hidden md:block px-4 py-2">
              <input
                  type="checkbox"
                  class="checkbox"
                  :checked="selectedIds?.includes(message._id)"
                  @change="toggleSelect(message._id)"
              />
            </div>
            <div class="flex items-center justify-center">
              <button
                  class="hidden md:flex w-10 h-10 hover:text-blue-600 hover:border hover:bg-white group border-gray-200 rounded-full items-center justify-center">
                <Reply class="group-hover:scale-110 transition-transform"/>
              </button>
            </div>
            <RouterLink :to="`/dashboard/messages/${message._id}`"
                        class="md:flex">
              <div class="px-4 py-2 select-none">{{ message.name }}</div>
              <div class="px-4 py-2 select-none">{{ store.truncateMessage(message.message) }}</div>
            </RouterLink>
          </div>
          <div class="px-4 py-2 select-none">{{ format_date(message.date) }}</div>
        </div>
      </template>
    </div>
  </div>
</template>