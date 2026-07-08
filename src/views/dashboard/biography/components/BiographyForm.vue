<script setup lang="ts">
import {useBiographyStore} from "@stores";
import {nextTick, onMounted, ref} from "vue";
import {storeToRefs} from "pinia";
import {X, Trash2, ListPlus, LayersPlus, Save, LoaderCircle, Check} from '@lucide/vue';

const store = useBiographyStore()
const {biography} = storeToRefs(store)
const saveStatus = ref<'idle' | 'loading' | 'saved' | 'error'>('idle')

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
const textareaRefs = ref<HTMLTextAreaElement[]>([])

const autoResize = (e: Event) => {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

const autoResizeAll = () => {
  textareaRefs.value.forEach(el => {
    if (!el) return
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
  })
}

onMounted(async () => {
  await store.fetchBiography('dashboard')
  await nextTick()
  autoResizeAll()
})
</script>

<template>
  <div v-if="biography" class="flex flex-col gap-6 mt-8 pb-24 md:pb-8">

    <!-- Main title -->
    <div>
      <label class="block font-bold text-xl mb-2">Main Title</label>
      <input v-model="biography.title" type="text"
             class="border border-gray-300 rounded px-4 py-2 w-full text-xl font-semibold font-unbounded"/>
    </div>

    <!-- Sections -->
    <div v-for="(section, sectionIndex) in biography.sections" :key="sectionIndex"
         class="border border-gray-200 bg-gray-50 rounded-xl p-4 md:p-6 flex flex-col gap-4">

      <!-- Section header -->
      <div class="flex flex-col gap-2 md:flex-row md:justify-between md:items-center">
        <label class="font-bold text-lg">Section {{ Number(sectionIndex) + 1 }}</label>
        <button @click="removeSection(Number(sectionIndex))"
                class="px-2 py-1 rounded-full text-red-500 text-sm hover:bg-red-100 transition flex items-center gap-1 self-start md:self-auto">
          <Trash2 class="w-4 h-4"/>
          Remove section
        </button>
      </div>

      <!-- Section title -->
      <input v-model="section.title" type="text" placeholder="Section title"
             class="bg-white border border-gray-300 rounded px-2 md:px-4 py-2 w-full font-semibold md:font-unbounded"/>

      <!-- Paragraphs -->
      <div v-for="(_, paragraphIndex) in section.paragraphs" :key="paragraphIndex"
           class="flex gap-2 items-start">
        <textarea
            v-model="section.paragraphs[paragraphIndex]"
            :ref="el => { if (el) textareaRefs[(sectionIndex as number) * 1000 + (paragraphIndex as number)] = el as HTMLTextAreaElement }"
            rows="3"
            @input="autoResize"
            placeholder="Paragraph content"
            class="bg-white border border-gray-300 rounded px-4 py-2 w-full min-h-10 resize-none overflow-hidden"
        />
        <button @click="removeParagraph(Number(sectionIndex), Number(paragraphIndex))"
                class="px-1 py-1 rounded-full text-red-500 text-sm hover:bg-red-100 hover:scale-105 border border-red-300 mt-2 transition">
          <X/>
        </button>
      </div>

      <button @click="addParagraph(Number(sectionIndex))"
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
    <div
        class="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200 md:relative md:bottom-auto md:left-auto md:right-auto md:p-0 md:border-0 md:bg-transparent flex flex-col items-center gap-4">
      <button @click="save"
              class="w-full md:w-auto bg-black text-white px-8 py-3 font-unbounded rounded-xl hover:bg-neutral-700 transition">
        <span v-if="saveStatus !== 'loading'" class="flex items-center justify-center gap-2"><Save/>Save</span>
        <span v-else class="flex items-center justify-center gap-2"><LoaderCircle class="animate-spin"/>Saving...</span>
      </button>
      <span v-if="saveStatus === 'saved'" class="text-green-600 text-sm flex items-center gap-2"><Check/>Saved successfully!</span>
      <span v-if="saveStatus === 'error'" class="text-red-500 text-sm flex items-center gap-2"><X/>An error occurred.</span>
    </div>

  </div>
</template>