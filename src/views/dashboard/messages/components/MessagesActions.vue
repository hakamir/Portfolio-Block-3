<script setup lang="ts">
import { Shredder, Trash2, Mail, Inbox } from '@lucide/vue';
import { useMessagesStore } from '@stores/messages'
import { storeToRefs } from 'pinia'

const props = defineProps<{ selectedIds: string[] }>()
const emit = defineEmits<{ 'update:selectedIds': [value: string[]] }>()

const store = useMessagesStore()
const { currentTab } = storeToRefs(store)

const markUnread = async () => {
  await store.applyToSelected(props.selectedIds, id => store.markAsRead(id, false))
  emit('update:selectedIds', [])
}
const moveToTrash = async () => {
  await store.applyToSelected(props.selectedIds, id => store.trashMessage(id, true))
  emit('update:selectedIds', [])
}
const moveToInbox = async () => {
  await store.applyToSelected(props.selectedIds, id => store.trashMessage(id, false))
  emit('update:selectedIds', [])
}
const deletePermanently = async () => {
  await store.applyToSelected(props.selectedIds, id => store.deleteMessage(id))
  emit('update:selectedIds', [])
}
</script>

<template>
  <div class="flex justify-start items-center">
    <div class="relative group flex justify-center items-center mx-2">
      <span class="tooltip">Mark as unread</span>
      <button @click="markUnread">
        <Mail />
      </button>
    </div>
    <div v-if="currentTab === 'inbox'" class="relative group flex justify-center items-center mx-2">
      <span class="tooltip">Move to trash</span>
      <button @click="moveToTrash">
        <Trash2 />
      </button>
    </div>
    <template v-if="currentTab === 'trash'">
      <div class="relative group flex justify-center items-center mx-2">
        <span class="tooltip">Permanently delete</span>
        <button @click="deletePermanently">
          <Shredder />
        </button>
      </div>
      <div class="relative group flex justify-center items-center mx-2">
        <span class="tooltip">Move to inbox</span>
        <button @click="moveToInbox">
          <Inbox />
        </button>
      </div>
    </template>
  </div>
</template>