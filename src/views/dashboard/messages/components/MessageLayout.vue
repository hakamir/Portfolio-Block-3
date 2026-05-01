<script setup lang="ts">
import MessagesTabs from "@views/dashboard/messages/components/MessagesTabs.vue";
import MessagesTable from "@views/dashboard/messages/components/MessagesTable.vue";
import MessagesActions from "@views/dashboard/messages/components/MessagesActions.vue";
import {useMessagesStore} from "@stores";
import {onMounted, ref} from "vue";


const store = useMessagesStore()
const selectedIds = ref<string[]>([])

onMounted(() => store.loadMessages())

</script>

<template>
  <MessagesActions class="md:flex hidden" v-model:selectedIds="selectedIds"/>
  <MessagesTabs class="flex justify-center md:justify-start"/>
  <MessagesTable v-model:selected-ids="selectedIds"/>
</template>

<style scoped>

</style>