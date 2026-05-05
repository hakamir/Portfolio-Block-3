<script setup lang="ts">
import AudioSection from "@views/dashboard/works/Components/AudioSection.vue";
import GallerySection from "@views/dashboard/works/Components/GallerySection.vue";
import type {Track} from "@stores";
import {ref, toRaw} from "vue";
import {Tag, Plus, Trash2} from "@lucide/vue";
import Modal from "@components/Modal.vue";

const selectedTrack = ref<Track | null>(null)
const tempTrack = ref<Track | null>(null)
const showTagEditionModal = ref(false)
const newTag = ref('')

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
  Object.assign(selectedTrack.value, tempTrack.value)

  showTagEditionModal.value = false
}

</script>

<template>

  <section class="pt-8 pb-16 md:pt-16 lg:container lg:mx-auto px-4 lg:px-32 flex flex-col gap-4">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Works</h1>
    <AudioSection @TagSelectorToggled="handleTagSelectorToggle"/>
    <GallerySection/>
    <Modal
        v-if="showTagEditionModal && tempTrack"
        :icon="Tag"
        :buttons="[
          { label: 'Cancel', type: 'cancel', action: () => showTagEditionModal = false },
          { label: 'Confirm', type: 'confirm', action: onConfirmTagEdition }
        ]"
        @close="showTagEditionModal = false"
    >
      <template #header>{{ tempTrack?.title }}</template>
      <div class="flex flex-col">
        <div v-for="(tag, index) in tempTrack.tags" :key="index" class="flex flex-col">
          <div class="flex">
            <input type="text"
                   disabled
                   class="border-x border-t border-gray-300/50 px-2 py-1 w-full focus:outline-none text-lg text-white"
                   :class="{'rounded-tl-2xl': index === 0}"
                   :value="tag">
            <button @click="removeTag(index)"
                    class="bg-red-700 hover:bg-red-800 transition border-t border-r border-gray-300/50 px-2 py-1"
                    :class="{'rounded-tr-2xl': index === 0}">
              <Trash2 class="text-white"/>
            </button>
          </div>
        </div>
        <div class="flex">
          <input type="text"
                 class="border-y border-l border-gray-300/50 px-2 py-1 w-full rounded-bl-2xl focus:outline-none text-lg placeholder:text-gray-400 placeholder:text-sm"
                 :class="{'rounded-tl-2xl': tempTrack.tags.length === 0}"
                 placeholder="Add a tag..."
                 v-model="newTag"/>
          <button @click="addTag()"
                  class="bg-lime-600 hover:bg-lime-700 transition px-2 py-1 rounded-br-2xl border border-gray-300/50"
                  :class="{'rounded-tr-2xl': tempTrack.tags.length === 0}">
            <Plus class="text-white"/>
          </button>
        </div>
      </div>
    </Modal>
  </section>
</template>

<style scoped>

</style>