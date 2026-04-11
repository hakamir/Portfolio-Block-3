<script setup lang="ts">
import OrphansAudio from "@views/dashboard/settings/components/OrphansAudio.vue";
import {ref} from "vue";
import {useAudioStore} from "@stores";
import {Trash2} from "@lucide/vue";
import Modal from "@components/Modal.vue";

const audioStore = useAudioStore()
const showDeleteModal = ref(false)
const orphansToDelete = ref<string[]>([])
const orphansRefreshKey = ref(0);

const onRequestDelete = (srcs: string[]) => {
  orphansToDelete.value = srcs
  showDeleteModal.value = true
}

const onConfirmDelete = async () => {
  await audioStore.deleteOrphans(orphansToDelete.value)
  showDeleteModal.value = false
  orphansToDelete.value = []
  orphansRefreshKey.value += 1;
}

</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-8 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Settings</h1>
    <OrphansAudio @request-delete="onRequestDelete" :key="orphansRefreshKey"/>
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
