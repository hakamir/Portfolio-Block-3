<script setup lang="ts">
import { ref, watch } from 'vue'
import { useMessagesStore } from '@stores/messages'
import { storeToRefs } from 'pinia'

const emit = defineEmits<{ (e: 'update:selectedIds', ids: string[]): void }>()

const store = useMessagesStore()
const { filteredMessages, fetchStatus } = storeToRefs(store)
const selectedIds = ref<string[]>([])
const expandedId = ref<string | null>(null)

const toggleSelect = (id: string, checked: boolean) => {
  selectedIds.value = checked
    ? [...selectedIds.value, id]
    : selectedIds.value.filter(i => i !== id)
  emit('update:selectedIds', selectedIds.value)
}

const toggleExpand = async (id: string) => {
  const message = filteredMessages.value.find(m => m._id === id)
  if (!message) return
  if (!message.read) await store.markAsRead(id, true)
  expandedId.value = expandedId.value === id ? null : id
}

// Réinitialise la sélection quand l'onglet change
watch(filteredMessages, () => {
  selectedIds.value = []
  emit('update:selectedIds', [])
})
</script>

<template>
  <table class="table">
    <thead>
      <tr>
        <th></th>
        <th>Name</th>
        <th>Email</th>
        <th>Message</th>
        <th>Date</th>
      </tr>
    </thead>
    <tbody>
      <!-- Loading -->
      <tr v-if="fetchStatus === 'loading'">
        <td colspan="5" class="text-center">
          <p class="flex justify-center m-4">Chargement...</p>
        </td>
      </tr>
      <!-- Error -->
      <tr v-else-if="fetchStatus === 'error'">
        <td colspan="5" class="text-center text-red-500">
          An error occurred while loading messages.
        </td>
      </tr>
      <!-- Empty -->
      <tr v-else-if="filteredMessages.length === 0">
        <td colspan="5" class="text-center">No messages found.</td>
      </tr>
      <!-- Messages -->
      <template v-else v-for="message in filteredMessages" :key="message._id">
        <tr
          @click="toggleExpand(message._id)"
          :class="{ 'font-bold': !message.read }"
          class="cursor-pointer">
          <td class="px-4 py-2" @click.stop>
            <input
              type="checkbox"
              class="checkbox"
              :checked="selectedIds.includes(message._id)"
              @change="(e) => toggleSelect(message._id, (e.target as HTMLInputElement).checked)"
            />
          </td>
          <td class="px-4 py-2 font-bold">{{ message.name }}</td>
          <td class="px-4 py-2">{{ message.email }}</td>
          <td class="px-4 py-2">{{ store.truncateMessage(message.message) }}</td>
          <td class="px-4 py-2">{{ new Date(message.date.$date).toLocaleString() }}</td>
        </tr>
        <!-- Expanded row -->
        <tr v-if="expandedId === message._id">
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
    </tbody>
  </table>
</template>