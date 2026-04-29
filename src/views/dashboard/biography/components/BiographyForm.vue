<script setup lang="ts">
import {useBiographyStore} from "@stores";
import {onMounted, ref} from "vue";
import {storeToRefs} from "pinia";
import {X, Trash2, ListPlus, LayersPlus, Save, LoaderCircle, Check} from '@lucide/vue';

const store = useBiographyStore()
const {biography} = storeToRefs(store)
const saveStatus = ref<'idle' | 'loading' | 'saved' | 'error'>('idle')


onMounted(async () => {
  await store.fetchBiography()
})

const addSection = () => {
  biography.value.sections.push({title: '', paragraphs: ['']})
}
const removeSection = (sectionIndex: number) => {
  biography.value.sections.splice(sectionIndex, 1)
}

const addParagraph = (sectionIndex: number) => {
  biography.value.sections[sectionIndex].paragraphs.push('')
}
const removeParagraph = (sectionIndex: number, paragraphIndex: number) => {
  biography.value.sections[sectionIndex].paragraphs.splice(paragraphIndex, 1)
}

const save = async () => {
  saveStatus.value = 'loading'
  try {
    await store.updateBiography()
    saveStatus.value = 'saved'
  } catch {
    saveStatus.value = 'error'
  }
}
</script>

<template>
  <div v-if="biography" class="flex flex-col gap-8 mt-8">

    <!-- Main title -->
    <div>
      <label class="block font-bold text-xl mb-2">Main Title</label>
      <input v-model="biography.title" type="text"
             class="border border-gray-300 rounded px-4 py-2 w-full text-xl font-semibold font-unbounded"/>
    </div>

    <!-- Sections -->
    <div v-for="(section, sectionIndex) in biography.sections" :key="sectionIndex"
         class="border border-gray-200 bg-gray-50 rounded-xl p-6 flex flex-col gap-4">
      <div class="flex justify-between items-center">
        <label class="font-bold text-lg">Section {{ sectionIndex + 1 }}</label>
        <button @click="removeSection(sectionIndex)"
                class="px-2 py-1 rounded-full text-red-500 text-sm hover:bg-red-100 transition flex items-center gap-1">
          <Trash2 class="w-4 h-4"/>
          Remove section
        </button>
      </div>

      <!-- Section title -->
      <input v-model="section.title" type="text" placeholder="Section title"
             class="bg-white border border-gray-300 rounded px-4 py-2 w-full font-semibold font-unbounded"/>

      <!-- Paragraphs -->
      <div v-for="(_, paragraphIndex) in section.paragraphs" :key="paragraphIndex"
           class="flex gap-2 items-start">
        <textarea v-model="section.paragraphs[paragraphIndex]" rows="3"
                  placeholder="Paragraph content"
                  class="bg-white border border-gray-300 rounded px-4 py-2 w-full min-h-10 resize-y"
                  style="font-size: 1.125rem;line-height: 1.75rem;"/>
        <button @click="removeParagraph(sectionIndex, paragraphIndex)"
                class="px-1 py-1 rounded-full text-red-500 text-sm hover:bg-red-100 hover:scale-105 border border-red-300 mt-2 transition">
          <X/>
        </button>
      </div>

      <button @click="addParagraph(sectionIndex)"
              class="px-2 py-1 rounded-xl text-sm text-blue-600 hover:bg-blue-100 self-start transition flex justify-center items-center gap-2">
        <ListPlus/>
        Add paragraph
      </button>
    </div>

    <!-- Add section button -->
    <button @click="addSection"
            class="border-2 border-dashed border-gray-300 rounded py-3 text-gray-500 hover:border-gray-400 hover:text-gray-600 hover:bg-gray-50 transition flex justify-center items-center gap-2">
      <LayersPlus/>
      Add section
    </button>

    <!-- Save -->
    <div class="flex flex-col items-center gap-4">
      <button @click="save"
              class="bg-black text-white px-8 py-3 font-unbounded rounded-xl hover:bg-neutral-700 transition ">

        <span v-if="saveStatus !== 'loading'" class="flex items-center gap-2"><Save />Save</span>
        <span v-else class="flex items-center gap-2"><LoaderCircle class="animate-spin" />Saving...</span>
      </button>
      <span v-if="saveStatus === 'saved'" class="text-green-600 text-sm flex items-center gap-2"><Check />Saved successfully !</span>
      <span v-if="saveStatus === 'error'" class="text-red-500 text-sm flex items-center gap-2"><X />An error occurred.</span>
    </div>

  </div>
</template>