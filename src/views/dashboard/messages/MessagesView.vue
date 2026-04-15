<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessagesStore } from '@stores'
import MessagesActions from './components/MessagesActions.vue'
import MessagesTabs from './components/MessagesTabs.vue'
import MessagesTable from './components/MessagesTable.vue'

const store = useMessagesStore()
const selectedIds = ref<string[]>([])

onMounted(() => store.loadMessages())
</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-8 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded">Messages</h1>
    <MessagesActions :selected-ids="selectedIds" />
    <MessagesTabs />
    <MessagesTable @update:selected-ids="ids => selectedIds = ids" />
  </section>
</template>