<script setup lang="ts">
import {type Message, useMessagesStore} from "@stores"
import {computed, onMounted, watch} from "vue"
import {useRoute} from "vue-router"
import {SearchX, Undo2, Trash2, Reply, Check, Undo} from "@lucide/vue"
import {buildMailtoLink} from "@utils/formatters.ts";
import Tooltip from "@components/layout/Tooltip.vue";


const route = useRoute()
const messageStore = useMessagesStore()

// Get current message by id
const message = computed(() =>
    messageStore.allMessages.find(m => m._id === route.params.id)
)

let hasMarked = false

const markAsReplied = async (msg: Message) => {
  if (!msg) return
  await messageStore.markAsReplied(msg._id, true)
}

const undoRepliedState = async (msg: Message) => {
  if (!msg) return
  await messageStore.markAsReplied(msg._id, false)
}

// In case the message is access directly without going through the inbox -> fetch messages
onMounted(async () => {
  if (!messageStore.allMessages.length) {
    await messageStore.fetchMessages()
  }
})

// Check if message is read and mark it as read if not
watch(() => message.value, async (msg) => {
      if (!msg || hasMarked) return
      if (!msg.read) {
        hasMarked = true
        await messageStore.markAsRead(msg._id, true)
      }
    }, {immediate: true}
)
</script>

<template>
  <div class="flex justify-between p-3">
    <Tooltip message="Back to inbox">
      <RouterLink to="/dashboard"
                  class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600 flex">
        <Undo2/>
      </RouterLink>
    </Tooltip>
    <div class="flex gap-4">
      <Tooltip message="Reply">
        <a v-if="message" :href="buildMailtoLink(message)" @click="markAsReplied(message)"
           class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600 flex">
          <Reply/>
        </a>
      </Tooltip>
      <Tooltip message="Move to trash">
        <button v-if="message"
                class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-red-600 flex">
          <Trash2/>
        </button>
      </Tooltip>
    </div>
  </div>

  <!-- Message Not Found -->
  <div v-if="!message">
    <SearchX class="w-24 h-24 text-gray-300 mx-auto"/>
    <h3 class="text-center font-unbounded text-3xl font-semibold text-gray-500">Message not found</h3>
  </div>

  <!-- Message Container -->
  <div v-else class="px-3">
    <div class="flex flex-col md:flex-row justify-between mb-4">
      <div class="flex items-center gap-3">
        <span class="font-semibold">{{ message.name }}</span>
        <span class="text-sm text-gray-500 select-none">
          <
          <a :href="`mailto:${message.email}`" class="hover:text-blue-600 hover:underline">{{ message.email }}</a>
          >
        </span>
      </div>
      <span class="text-sm text-gray-500">{{ message.date }}</span>
    </div>
    <div>
      {{ message.message }}
    </div>
    <div v-if="message.replied" class="mt-8 flex">
      <span
          class="flex items-center gap-2 px-3 py-1 border border-gray-300 bg-white rounded-full">
        <Check class="text-primary-700"/>
        <span class="select-none text-gray-700">You have replied to this message</span>
        <Tooltip message="Unmark as replied">
          <button @click="undoRepliedState(message)"
                  class="hover:scale-105 transition hover:text-primary-700 flex items-center">
            <Undo/>
          </button>
        </Tooltip>
      </span>
    </div>
    <div class="flex py-2" :class="{ 'mt-8': !message.replied }">
      <a :href="buildMailtoLink(message)" @click="markAsReplied(message)"
         class="flex gap-2 px-3 py-1 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600">
        <Reply/>
        <span class="select-none">Answer</span>
      </a>
    </div>
  </div>
</template>

<style scoped>

</style>