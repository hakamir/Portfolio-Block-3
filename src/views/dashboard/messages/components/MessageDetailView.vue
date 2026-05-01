<script setup lang="ts">
import {useMessagesStore} from "@stores"
import {computed, onMounted, watch} from "vue"
import {useRoute} from "vue-router"
import {SearchX, Undo2, Trash2, Reply} from "@lucide/vue"

const route = useRoute()
const messageStore = useMessagesStore()
const message = computed(() =>
    messageStore.allMessages.find(m => m._id === route.params.id)
)

let hasMarked = false

onMounted(async () => {
  if (!messageStore.allMessages.length) {
    await messageStore.loadMessages()
  }
})

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
  <div class="flex justify-between">
    <RouterLink to="/dashboard"
                class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600">
      <Undo2/>
    </RouterLink>
    <div class="flex gap-4">
      <button class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600">
        <Reply/>
      </button>
      <button class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-red-600">
        <Trash2/>
      </button>
    </div>
  </div>

  <!-- Message Not Found -->
  <div v-if="!message">
    <SearchX class="w-24 h-24 text-gray-300 mx-auto"/>
    <h3 class="text-center font-unbounded text-3xl font-semibold text-gray-500">Message not found</h3>
  </div>

  <!-- Message Container -->
  <div v-else>
    <div class="flex justify-between items-center mb-4">
      <h3 class="flex items-center gap-3">
        <span class="font-semibold">{{ message.name }}</span>
        <span class="text-sm text-gray-500 select-none">
          <
          <a :href="`mailto:${message.email}`" class="hover:text-blue-600 hover:underline">{{ message.email }}</a>
          >
        </span>
      </h3>
      <span class="text-sm text-gray-500">{{ message.date }}</span>
    </div>
    <div>
      {{ message.message }}
    </div>
    <div class="mt-8">
      <button
          class="flex gap-2 px-3 py-1 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600">
        <Reply/>
        Answer
      </button>
    </div>
  </div>
</template>

<style scoped>

</style>