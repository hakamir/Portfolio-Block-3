<script setup lang="ts">
import AudioSection from "@views/dashboard/works/Components/AudioSection.vue";
import GallerySection from "@views/dashboard/works/Components/GallerySection.vue";
import {type Track, useArtistsStore} from "@stores";
import {ref, toRaw} from "vue";
import {Tag, Plus, X} from "@lucide/vue";
import Modal from "@components/Modal.vue";
import {onBeforeRouteLeave} from "vue-router";
import {useGalleriesStore} from "@stores/gallery.ts";

const selectedTrack = ref<Track | null>(null)
const tempTrack = ref<Track | null>(null)
const showTagEditionModal = ref(false)
const newTag = ref('')
const artistsStore = useArtistsStore()
const galleriesStore = useGalleriesStore()
const showUnsavedChangesModal = ref(false)
let resolveNavigation: ((confirm: boolean) => void) | null = null

onBeforeRouteLeave(() => {
  if (!artistsStore.isDirty && !galleriesStore.isDirty) return true

  showUnsavedChangesModal.value = true
  return new Promise(resolve => {
    resolveNavigation = resolve
  })
})

const onConfirmLeave = () => {
  showUnsavedChangesModal.value = false
  resolveNavigation?.(true)
}

const onCancelLeave = () => {
  showUnsavedChangesModal.value = false
  resolveNavigation?.(false)
}

const handleTagSelectorToggle = (track: Track) => {
  selectedTrack.value = track
  tempTrack.value = structuredClone(toRaw(track))
  if (!tempTrack.value.tags) tempTrack.value.tags = []
  showTagEditionModal.value = true
}

const addTag = () => {
  if (!tempTrack.value) return

  const value = newTag.value.trim()
  if (!value) return

  tempTrack.value.tags.push(value)
  newTag.value = ''
}

const removeTag = (index: number) => {
  tempTrack.value?.tags.splice(index, 1)
}

const onConfirmTagEdition = () => {
  if (!selectedTrack.value || !tempTrack.value) return
  const pending = newTag.value.trim()
  if (pending) {
    tempTrack.value.tags.push(pending)
    newTag.value = ''
  }
  Object.assign(selectedTrack.value, tempTrack.value)
  showTagEditionModal.value = false
}
</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 lg:container lg:mx-auto px-4 lg:px-32 flex flex-col gap-4">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Works</h1>
    <AudioSection @TagSelectorToggled="handleTagSelectorToggle"/>
    <GallerySection/>

    <!-- Tag edition modal -->
    <Modal v-if="showTagEditionModal && tempTrack"
           :icon="Tag"
           :buttons="[{ label: 'Cancel', color: 'white', action: () => showTagEditionModal = false },
                      { label: 'Confirm', color: 'green', action: onConfirmTagEdition }]"
           @close="showTagEditionModal = false">
      <template #header>{{ tempTrack.title }}</template>
      <div class="flex flex-col gap-4">
        <div class="flex flex-wrap gap-2 min-h-10">
          <span v-if="tempTrack.tags.length === 0" class="text-gray-400 text-sm italic">No tags yet</span>
          <span v-for="(tag, index) in tempTrack.tags"
                :key="index"
                class="flex items-center gap-1 bg-gray-100 border border-gray-300 text-sm px-3 py-1 rounded-full">
            {{ tag }}
            <button @click="removeTag(index)"
                    class="w-6 h-6 p-1 flex items-center justify-center rounded-full text-gray-400 hover:text-red-600 hover:bg-red-100 transition ml-1">
              <X/>
            </button>
          </span>
        </div>
        <div class="flex gap-2">
          <input type="text"
                 class="border border-gray-300 rounded-xl px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-lime-500 text-sm"
                 placeholder="Add a tag..."
                 v-model="newTag"
                 @keydown.enter.prevent="addTag"/>
          <button @click="addTag"
                  class="bg-lime-600 hover:bg-lime-700 transition px-3 py-2 rounded-xl border border-gray-300/50 shrink-0">
            <Plus class="text-white w-4 h-4"/>
          </button>
        </div>
      </div>
    </Modal>

    <!-- Confirm leave modal -->
    <Modal v-if="showUnsavedChangesModal"
           :buttons="[{ label: 'Stay', color: 'blue', action: onCancelLeave },
                  { label: 'Leave anyway', color: 'white', action: onConfirmLeave }]"
           @close="onCancelLeave" :closeOnBackdrop="true">
      <template #header>Unsaved changes</template>
      <p class="text-sm text-gray-800">You have unsaved changes. Are you sure you want to leave?</p>
    </Modal>
  </section>
</template>

<style scoped>

</style>