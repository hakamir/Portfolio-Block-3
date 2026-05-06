<script setup lang="ts">
import OrphansAudio from "@views/dashboard/settings/components/OrphansAudio.vue";
import {ref} from "vue";
import {useAudioStore} from "@stores";
import {Trash2} from "@lucide/vue";
import Modal from "@components/Modal.vue";
import ChangePassword from "@views/dashboard/settings/components/ChangePassword.vue";

const audioStore = useAudioStore()
const showDeleteModal = ref(false)
const orphansToDelete = ref<string[]>([])

// Receive delete request from child and open confirmation modal with selected items
const onRequestDelete = (srcs: string[]) => {
  orphansToDelete.value = srcs
  showDeleteModal.value = true
}

// Confirm deletion, call store, then reset modal state and trigger list refresh
const onConfirmDelete = async () => {
  await audioStore.deleteOrphans(orphansToDelete.value)
  showDeleteModal.value = false
  orphansToDelete.value = []
}

</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-4 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Settings</h1>
    <div class="flex flex-col gap-8">
      <ChangePassword/>
      <OrphansAudio @request-delete="onRequestDelete"/>
    </div>
    <Modal
        v-if="showDeleteModal"
        :icon="Trash2"
        :buttons="[
          { label: 'Cancel', type: 'cancel', action: () => showDeleteModal = false },
          { label: 'Delete', type: 'delete', action: onConfirmDelete }
        ]"
        @close="showDeleteModal = false"
    >
      <template #header>Confirm deletion</template>
      You are about to permanently delete
      <span class="font-semibold text-red-600">{{ orphansToDelete.length }} file{{
          orphansToDelete.length > 1 ? 's' : ''
        }}</span>.
      This action cannot be undone.
    </Modal>
  </section>
</template>
