<script setup lang="ts">
import OrphansAudio from "@views/dashboard/settings/components/OrphansAudio.vue";
import {ref} from "vue";
import {useAuthStore, useOrphansStore} from "@stores";
import {Trash2, RotateCcw} from "@lucide/vue";
import Modal from "@components/Modal.vue";
import ChangePassword from "@views/dashboard/settings/components/ChangePassword.vue";
import OrphansGallery from "@views/dashboard/settings/components/OrphansGallery.vue";
import Backgrounds from "@views/dashboard/settings/components/Backgrounds.vue";
const orphansStore = useOrphansStore()
const showAudioDeleteModal = ref(false)
const orphansAudioToDelete = ref<string[]>([])
const orphansAudioRefreshKey = ref(0);
const showAudioRollbackModal = ref(false)
const orphansAudioToRollback = ref<string[]>([])
const rollbackResult = ref<{ restored: string[], failed: { id: string, title: string, error: string }[] } | null>(null)

// Receive delete request from child and open confirmation modal with selected items
const onAudioRequestDelete = (srcs: string[]) => {
  orphansAudioToDelete.value = srcs
  showAudioDeleteModal.value = true
}

// Confirm deletion, call store, then reset modal state and trigger list refresh
const onAudioConfirmDelete = async () => {
  await orphansStore.deleteOrphans(orphansAudioToDelete.value)
  showAudioDeleteModal.value = false
  orphansAudioToDelete.value = []
  orphansAudioRefreshKey.value += 1;
}

const showGalleryDeleteModal = ref(false)
const orphansGalleryToDelete = ref<string[]>([])
const orphansGalleryRefreshKey = ref(0);
const showGalleryRollbackModal = ref(false)
const orphansGalleryToRollback = ref<string[]>([])
const rollbackGalleryResult = ref<{ restored: string[], failed: { id: string, title: string, error: string }[] } | null>(null)

const onGalleryRequestDelete = (ids: string[]) => {
  orphansGalleryToDelete.value = ids
  showGalleryDeleteModal.value = true
}

const onGalleryConfirmDelete = async () => {
  await orphansStore.deleteOrphanGalleries(orphansGalleryToDelete.value)
  showGalleryDeleteModal.value = false
  orphansGalleryToDelete.value = []
  orphansGalleryRefreshKey.value += 1
}

const onGalleryRequestRollback = (ids: string[]) => {
  orphansGalleryToRollback.value = ids
  showGalleryRollbackModal.value = true
}

const onGalleryConfirmRollback = async () => {
  const result = await orphansStore.rollbackOrphanGalleries(orphansGalleryToRollback.value)
  showGalleryRollbackModal.value = false
  rollbackGalleryResult.value = result
  orphansGalleryToRollback.value = []
  orphansGalleryRefreshKey.value += 1
}

const onAudioRequestRollback = (srcs: string[]) => {
  orphansAudioToRollback.value = srcs
  showAudioRollbackModal.value = true
}

const onAudioConfirmRollback = async () => {
  const result = await orphansStore.rollbackOrphans(orphansAudioToRollback.value)
  showAudioRollbackModal.value = false
  rollbackResult.value = result
  orphansAudioToRollback.value = []
  orphansAudioRefreshKey.value += 1
}

const authStore = useAuthStore()
const role = authStore.payload?.role ?? ""
</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-4 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Settings</h1>
    <div class="flex flex-col gap-8">
      <ChangePassword/>
      <OrphansAudio v-if="role !== 'admin'" @request-delete="onAudioRequestDelete" @request-rollback="onAudioRequestRollback"
                    :key="orphansAudioRefreshKey"/>
      <OrphansGallery v-if="role !== 'admin'"  @request-delete="onGalleryRequestDelete" @request-rollback="onGalleryRequestRollback"
                    :key="orphansGalleryRefreshKey"/>
      <Backgrounds v-if="role !== 'admin'" />
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

    <!-- Modal for gallery rollback confirmation -->
    <Modal
        v-if="showGalleryRollbackModal"
        :icon="RotateCcw"
        :buttons="[
          { label: 'Cancel', color: 'white', action: () => showGalleryRollbackModal = false },
          { label: 'Restore', color: 'green', action: onGalleryConfirmRollback }
        ]"
        @close="showGalleryRollbackModal = false"
    >
      <template #header>Confirm restore</template>
      You are about to restore
      <span class="font-semibold text-green-600">{{ orphansGalleryToRollback.length }} image{{
          orphansGalleryToRollback.length > 1 ? 's' : ''
        }}</span>
      to the database.<br><br> Their metadata will be reconstructed from the previous versions.
    </Modal>

    <!-- Modal for gallery rollback result -->
    <Modal
        v-if="rollbackGalleryResult"
        :icon="RotateCcw"
        :buttons="[
          { label: 'Close', color: 'white', action: () => rollbackGalleryResult = null }
        ]"
        @close="rollbackGalleryResult = null"
    >
      <template #header>Restore complete</template>
      <div class="flex flex-col gap-2">
        <p>
          <span class="font-semibold text-green-600">{{ rollbackGalleryResult.restored.length }} image{{
              rollbackGalleryResult.restored.length > 1 ? 's' : ''
            }} restored</span> successfully.
        </p>
        <div v-if="rollbackGalleryResult?.failed.length > 0">
          <p class="font-semibold text-red-600 mb-1">
            {{ rollbackGalleryResult.failed.length }} image{{ rollbackGalleryResult.failed.length > 1 ? 's' : '' }} failed :
          </p>
          <ul class="text-sm text-red-500 list-disc list-inside">
            <li v-for="f in rollbackGalleryResult?.failed" :key="f.id">
              <span class="font-mono">{{ f.title }}</span> — {{ f.error }}
            </li>
          </ul>
        </div>
      </div>
    </Modal>

    <!-- Modal for audio rollback confirmation -->
    <Modal
        v-if="showAudioRollbackModal"
        :icon="RotateCcw"
        :buttons="[
      { label: 'Cancel', color: 'white', action: () => showAudioRollbackModal = false },
      { label: 'Restore', color: 'green', action: onAudioConfirmRollback }
    ]"
        @close="showAudioRollbackModal = false"
    >
      <template #header>Confirm restore</template>
      You are about to restore
      <span class="font-semibold text-green-600">{{ orphansAudioToRollback.length }} file{{
          orphansAudioToRollback.length > 1 ? 's' : ''
        }}</span>
      to the database.<br><br> Their metadata will be reconstructed from the previous versions.
    </Modal>

    <!-- Modal for audio rollback result -->
    <Modal
        v-if="rollbackResult"
        :icon="RotateCcw"
        :buttons="[
      { label: 'Close', color: 'white', action: () => rollbackResult = null }
    ]"
        @close="rollbackResult = null"
    >
      <template #header>Restore complete</template>
      <div class="flex flex-col gap-2">
        <p>
      <span class="font-semibold text-green-600">{{ rollbackResult.restored.length }} file{{
          rollbackResult.restored.length > 1 ? 's' : ''
        }} restored</span> successfully.
        </p>
        <div v-if="rollbackResult?.failed.length > 0">
          <p class="font-semibold text-red-600 mb-1">
            {{ rollbackResult.failed.length }} file{{ rollbackResult.failed.length > 1 ? 's' : '' }} failed :
          </p>
          <ul class="text-sm text-red-500 list-disc list-inside">
            <li v-for="f in rollbackResult?.failed" :key="f.id">
              <span class="font-mono">{{ f.title }}</span> — {{ f.error }}
            </li>
          </ul>
        </div>
      </div>
    </Modal>
  </section>
</template>
