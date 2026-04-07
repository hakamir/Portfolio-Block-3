<script setup lang="ts">
import {useMessagesStore} from '@stores/messages'
import {storeToRefs} from 'pinia'

const store = useMessagesStore()
const {currentTab} = storeToRefs(store)
</script>

<template>
  <div class="flex gap-4 mt-8">
    <button
        @click="currentTab = 'inbox'"
        :class="currentTab === 'inbox'
        ? 'border-primary-700 text-success'
        : 'border-transparent text-gray-500'"
        class="tab-button px-4 py-2 font-semibold border-b-2 hover:text-gray-700">
      Inbox
    </button>
    <button
        @click="currentTab = 'trash'"
        :class="currentTab === 'trash'
        ? 'border-primary-700 text-success'
        : 'border-transparent text-gray-500'"
        class="tab-button px-4 py-2 font-semibold border-b-2 hover:text-gray-700">
      Trash
    </button>
  </div>
</template>