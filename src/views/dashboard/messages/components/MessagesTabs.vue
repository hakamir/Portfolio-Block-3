<script setup lang="ts">
import {useMessagesStore} from '@stores/messages'
import {storeToRefs} from 'pinia'
import {Inbox, Trash2} from "@lucide/vue";

const store = useMessagesStore()
const {currentTab} = storeToRefs(store)
</script>

<template>
  <div class="flex gap-4 mt-8 md:ml-8">
    <button
        @click="currentTab = 'inbox'"
        :class="currentTab === 'inbox'
        ? 'border-black text-blue-600 hover:text-blue-700'
        : 'border-transparent text-gray-500 hover:text-gray-700'"
        class="tab-button px-4 py-2 font-semibold border-b-3 flex items-center gap-2">
      <Inbox/>
      Inbox
    </button>
    <button
        @click="currentTab = 'trash'"
        :class="currentTab === 'trash'
        ? 'border-black text-blue-600 hover:text-blue-700'
        : 'border-transparent text-gray-500 hover:text-gray-700'"
        class="tab-button px-4 py-2 font-semibold border-b-3 flex items-center gap-2">
      <Trash2/>
      Trash
    </button>
  </div>
</template>