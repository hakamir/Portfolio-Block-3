<script setup lang="ts">
import {ref, watch} from 'vue'
import {useMessagesStore} from '@stores/messages'
import {storeToRefs} from 'pinia'
import {Inbox, Mail, Trash2, Shredder} from "@lucide/vue";
import {format_date} from "@utils/formatters.ts";

const props = defineProps<{ selectedIds: string[] }>()
const emit = defineEmits<{ 'update:selectedIds': [value: string[]] }>()

const store = useMessagesStore()
const {filteredMessages, fetchStatus} = storeToRefs(store)

// Toggle the selection of a message
const toggleSelect = (id: string) => {
  const set = new Set(props.selectedIds)
  if (set.has(id)) set.delete(id)
  else set.add(id)
  emit('update:selectedIds', [...set])
}

// Reset selectedIds when the filteredMessages change
watch(filteredMessages, () => {
  emit('update:selectedIds', [])
})

// Track the swipe state for each message (by id)
const swipeState = ref<Record<string, {
  startX: number
  startY: number
  deltaX: number
  swiping: boolean
  locked: boolean
}>>({})

// Initialize swipe state with the initial touch position
const onTouchStart = (id: string, e: TouchEvent) => {
  swipeState.value[id] = {
    startX: e.touches[0].clientX,
    startY: e.touches[0].clientY,
    deltaX: 0,
    swiping: false,
    locked: false
  }
}

// Detect swipe direction, ignore small movements (5px), lock vertical gestures, and handle horizontal swipe
const onTouchMove = (id: string, e: TouchEvent) => {
  const state = swipeState.value[id]
  if (!state) return

  const deltaX = e.touches[0].clientX - state.startX
  const deltaY = e.touches[0].clientY - state.startY

  if (!state.swiping && Math.abs(deltaX) < 5 && Math.abs(deltaY) < 5) return

  if (!state.swiping && Math.abs(deltaY) > Math.abs(deltaX)) {
    swipeState.value[id] = {...state, swiping: false, deltaX: 0, locked: true}
    return
  }

  if (state.locked) return

  e.preventDefault()
  swipeState.value[id] = {...state, swiping: true, deltaX}
}

// Trigger actions based on swipe distance and direction (threshold 200px), depending on the current tab, then reset selection and swipe state
const onTouchEnd = async (id: string) => {
  const state = swipeState.value[id]
  const delta = state?.deltaX ?? 0
  if (store.currentTab == "inbox") {
    if (delta > 200) {
      await store.markAsRead(id, false)
    } else if (delta < -200) {
      await store.markAsTrashed(id, true)
    }
  } else if (store.currentTab == "trash") {
    if (delta > 200) {
      await store.markAsTrashed(id, false)
    } else if (delta < -200) {
      await store.deleteMessage(id)
    }
  }
  emit('update:selectedIds', [])
  swipeState.value[id] = {startX: 0, startY: 0, deltaX: 0, locked: false, swiping: false}
}

// Return the current horizontal swipe offset
const getSwipeDelta = (id: string) => swipeState.value[id]?.deltaX ?? 0

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
        <div class="relative flex border-b border-neutral-200 overflow-hidden">

          <!-- Mark as read (Mobile) -->
          <div class="flex items-center justify-end bg-blue-600 text-white overflow-hidden transition-all duration-75"
               :style="{ width: `${Math.max(0, getSwipeDelta(message._id))}px` }">
            <Mail v-if="store.currentTab === 'inbox'" class="mr-4"/>
            <Inbox v-else class="mr-4"/>
          </div>

          <!-- Message -->
          <div :class="[!message.read ? 'font-bold bg-blue-50' : 'bg-white',
                !swipeState[message._id]?.swiping ? 'transition-all duration-200' : '']"
               class="flex-1 cursor-pointer flex justify-between hover:bg-gray-50 min-w-0"
               @touchstart="onTouchStart(message._id, $event)"
               @touchmove="onTouchMove(message._id, $event)"
               @touchend="onTouchEnd(message._id)"
          >
            <div class="flex min-w-0">
              <div class="hidden md:block px-4 py-2">
                <input
                    type="checkbox"
                    class="checkbox"
                    :checked="selectedIds?.includes(message._id)"
                    @change="toggleSelect(message._id)"
                    aria-label="Select message"
                />
              </div>
              <RouterLink :to="`/dashboard/messages/${message._id}`" class="md:flex min-w-0" aria-label="View message">
                <div class="px-4 py-2 select-none truncate min-w-50 font-medium">{{ message.name }}</div>
                <div class="px-4 py-2 select-none truncate text-sm md:text-base">{{ message.message }}</div>
              </RouterLink>
            </div>
            <div class="flex items-center justify-end gap-2">
              <div v-if="message.replied" class=" px-2 py-1 bg-primary/10 border border-primary-700/50  rounded-full">
                <span class="text-sm text-primary-800/70">Replied</span>
              </div>
              <div class="px-4 py-2 select-none shrink-0">{{ format_date(message.date) }}</div>
            </div>
          </div>

          <!-- Trash (Mobile) -->
          <div class="flex items-center justify-start bg-red-600 text-white overflow-hidden transition-all duration-75"
               :style="{ width: `${Math.max(0, -getSwipeDelta(message._id))}px` }">
            <Trash2 v-if="store.currentTab === 'inbox'" class="ml-4"/>
            <Shredder v-else class="ml-4"/>
          </div>

        </div>
      </template>
    </div>
  </div>
</template>