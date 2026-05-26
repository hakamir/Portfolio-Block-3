<script setup lang="ts">
import {Shredder, Trash2, Mail, Inbox} from '@lucide/vue';
import {useMessagesStore} from '@stores/messages'
import {storeToRefs} from 'pinia'
import Tooltip from "@components/layout/Tooltip.vue";
import MessageSearchEngine from "@views/dashboard/messages/components/MessageSearchEngine.vue";

const props = defineProps<{ selectedIds: string[] }>()
const emit = defineEmits<{ 'update:selectedIds': [value: string[]] }>()

const store = useMessagesStore()
const {currentTab} = storeToRefs(store)

const markUnread = async () => {
  await store.applyToSelected(props.selectedIds, id => store.markAsRead(id, false))
  emit('update:selectedIds', [])
}
const moveToTrash = async () => {
  await store.applyToSelected(props.selectedIds, id => store.markAsTrashed(id, true))
  emit('update:selectedIds', [])
}
const moveToInbox = async () => {
  await store.applyToSelected(props.selectedIds, id => store.markAsTrashed(id, false))
  emit('update:selectedIds', [])
}
const deletePermanently = async () => {
  await store.applyToSelected(props.selectedIds, id => store.deleteMessage(id))
  emit('update:selectedIds', [])
}
</script>

<template>
  <div class="flex justify-start items-center gap-2">
    <Tooltip message="Mark as unread">
      <button @click="markUnread" aria-label="Mark as unread" class="action-button hover:text-blue-600 transition">
        <Mail/>
      </button>
    </Tooltip>
    <Tooltip message="Move to trash" v-if="currentTab === 'inbox'">
      <button @click="moveToTrash" class="action-button hover:text-red-600 transition" aria-label="Move to trash">
        <Trash2/>
      </button>
    </Tooltip>
    <template v-if="currentTab === 'trash'">
      <Tooltip message="Permanently delete">
        <button @click="deletePermanently" class="action-button hover:text-red-600 transition" aria-label="Permanently delete">
          <Shredder/>
        </button>
      </Tooltip>
      <Tooltip message="Move to inbox">
        <button @click="moveToInbox" class="action-button hover:text-blue-600 transition" aria-label="Move to inbox">
          <Inbox/>
        </button>
      </Tooltip>
    </template>
    <MessageSearchEngine/>
  </div>
</template>