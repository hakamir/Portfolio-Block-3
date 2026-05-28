<script setup lang="ts">
import OrphansAudio from "@views/dashboard/settings/components/OrphansAudio.vue";
import {ref} from "vue";
import {useAudioStore} from "@stores";
import {Trash2} from "@lucide/vue";
import Modal from "@components/Modal.vue";
import ChangePassword from "@views/dashboard/settings/components/ChangePassword.vue";
import OrphansGallery from "@views/dashboard/settings/components/OrphansGallery.vue";
import Backgrounds from "@views/dashboard/settings/components/Backgrounds.vue";
import {useGalleriesStore} from "@stores/gallery.ts";

const audioStore = useAudioStore()
const showAudioDeleteModal = ref(false)
const orphansAudioToDelete = ref<string[]>([])
const orphansAudioRefreshKey = ref(0);

// Receive delete request from child and open confirmation modal with selected items
const onAudioRequestDelete = (srcs: string[]) => {
  orphansAudioToDelete.value = srcs
  showAudioDeleteModal.value = true
}

// Confirm deletion, call store, then reset modal state and trigger list refresh
const onAudioConfirmDelete = async () => {
  await audioStore.deleteOrphans(orphansAudioToDelete.value)
  showAudioDeleteModal.value = false
  orphansAudioToDelete.value = []
  orphansAudioRefreshKey.value += 1;
}

const galleryStore = useGalleriesStore()
const showGalleryDeleteModal = ref(false)
const orphansGalleryToDelete = ref<string[]>([])
const orphansGalleryRefreshKey = ref(0);

const onGalleryRequestDelete = (srcs: string[]) => {
  orphansGalleryToDelete.value = srcs
  console.log(orphansGalleryToDelete.value)
  showGalleryDeleteModal.value = true
}

const onGalleryConfirmDelete = async () => {
  await galleryStore.deleteOrphans(orphansGalleryToDelete.value)
  showGalleryDeleteModal.value = false
  orphansGalleryToDelete.value = []
  orphansGalleryRefreshKey.value += 1;
}

</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-4 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Settings</h1>
    <div class="flex flex-col gap-8">
      <ChangePassword/>
      <OrphansAudio @request-delete="onAudioRequestDelete" :key="orphansAudioRefreshKey"/>
      <OrphansGallery @request-delete="onGalleryRequestDelete" :key="orphansGalleryRefreshKey"/>
      <Backgrounds/>
    </div>
    <!-- Modal for audio deletion confirmation -->
    <Modal
        v-if="showAudioDeleteModal"
        :icon="Trash2"
        :buttons="[
          { label: 'Cancel', color: 'white', action: () => showAudioDeleteModal = false },
          { label: 'Delete', color: 'red', action: onAudioConfirmDelete }
        ]"
        @close="showAudioDeleteModal = false"
    >
      <template #header>Confirm deletion</template>
      You are about to permanently delete
      <span class="font-semibold text-red-600">{{ orphansAudioToDelete.length }} file{{
          orphansAudioToDelete.length > 1 ? 's' : ''
        }}</span>.
      This action cannot be undone.
    </Modal>

    <!-- Modal for gallery deletion confirmation -->
    <Modal
        v-if="showGalleryDeleteModal"
        :icon="Trash2"
        :buttons="[
          { label: 'Cancel', color: 'white', action: () => showGalleryDeleteModal = false },
          { label: 'Delete', color: 'red', action: onGalleryConfirmDelete }
        ]"
        @close="showGalleryDeleteModal = false"
    >
      <template #header>Confirm deletion</template>
      You are about to permanently delete
      <span class="font-semibold text-red-600">{{ orphansGalleryToDelete.length }} file{{
          orphansGalleryToDelete.length > 1 ? 's' : ''
        }}</span>.
      This action cannot be undone.
    </Modal>
  </section>
</template>
