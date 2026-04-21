<script setup lang="ts">
import {ref, watch} from 'vue'
import {useMessagesStore} from '@stores/messages'
import {storeToRefs} from 'pinia'
import {Reply} from "@lucide/vue";

const props = defineProps<{ selectedIds: string[] }>()
const emit = defineEmits<{ 'update:selectedIds': [value: string[]] }>()

const store = useMessagesStore()
const {filteredMessages, fetchStatus} = storeToRefs(store)
const expandedId = ref<string | null>(null)

const toggleSelect = (id: string) => {
  const set = new Set(props.selectedIds)
  if (set.has(id)) set.delete(id)
  else set.add(id)
  emit('update:selectedIds', [...set])
}

const toggleExpand = async (id: string) => {
  const message = filteredMessages.value.find(m => m._id === id)
  if (!message) return
  if (!message.read) await store.markAsRead(id, true)
  expandedId.value = expandedId.value === id ? null : id
}

watch(filteredMessages, () => {
  emit('update:selectedIds', [])
})

const format_date = (date: Date) => {
  date = new Date(date)
  const now = new Date()
  const diff = (now.getTime() - date.getTime()) / 1000
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`
  if (diff < 86400) return date.toLocaleTimeString()
  if (now.getFullYear() === date.getFullYear()) return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric'
  }).format(date)
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
        <div
            @click="toggleExpand(message._id)"
            :class="!message.read ? 'font-bold bg-blue-50': 'bg-white'"
            class="cursor-pointer border-b border-neutral-200 flex justify-between hover:bg-gray-50">
          <div class="flex">
            <div class="px-4 py-2" @click.stop>
              <input
                  type="checkbox"
                  class="checkbox"
                  :checked="selectedIds?.includes(message._id)"
                  @change="toggleSelect(message._id)"
              />
            </div>
            <div class="flex items-center justify-center ">
              <button @click.stop
                      class="w-10 h-10 hover:text-blue-600 hover:border hover:bg-white group border-gray-200 rounded-full flex items-center justify-center">
                <Reply class="group-hover:scale-110 transition-transform"/>
              </button>
            </div>
            <div class="px-4 py-2 select-none">{{ message.name }}</div>
            <div class="px-4 py-2 select-none">{{ store.truncateMessage(message.message) }}</div>
          </div>
          <div class="px-4 py-2 select-none">{{ format_date(message.date.$date) }}</div>
        </div>
        <!-- Expanded row -->
        <tr v-if="expandedId === message._id" class="border-b border-neutral-200">
          <td colspan="5" class="px-4 py-2 bg-gray-50">
            <div class="flex justify-between">
              <div>
                <span class="font-bold text-lg">{{ message.name }}</span>
                <a :href="`mailto:${message.email}`" class="text-gray-500 hover:underline ml-2">
                  {{ message.email }}
                </a>
              </div>
              <span class="text-gray-500 italic">{{ new Date(message.date.$date).toLocaleString() }}</span>
            </div>
            <p class="whitespace-pre-wrap mt-2">{{ message.message }}</p>
          </td>
        </tr>
      </template>
    </div>
  </div>
</template>