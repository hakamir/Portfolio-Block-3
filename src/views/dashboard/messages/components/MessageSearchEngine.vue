<script setup lang="ts">
import {Search} from "@lucide/vue";
import {computed, ref} from "vue";
import {useMessagesStore} from "@stores";
import {type MessageSearchResult, useMessageSearch} from "@composables/useMessageSearch.ts";
import {useRouter} from "vue-router";

const messageStore = useMessagesStore()
const {search} = useMessageSearch(() => messageStore.filteredMessages)
const query = ref('')
const showResults = ref(false)
const results = computed(() => search(query.value))
const router = useRouter()

const navigateToMessage = (result: MessageSearchResult) => {
  router.push(`/dashboard/messages/${result.id}`)
  query.value = ''
  showResults.value = false
}

const onInput = () => {
  showResults.value = query.value.trim().length > 0
}

const onBlur = () => {
  setTimeout(() => {
    showResults.value = false
  }, 150)
}
</script>

<template>
  <div class="relative">
    <div class="flex items-center border rounded-full w-50 bg-white h-14 border-gray-300 group
                focus-within:w-100 focus-within:inset-shadow-[0_0_5px_rgba(0,0,0,0.5)]
                focus-within:bg-white/70 ring-inset ring-black/50
                transition-[width,box-shadow,background-color] duration-300">
      <label v-if="!query.trim()" for="search"
             class="absolute flex gap-4 font-unbounded px-4 transition select-none
                    group-focus-within:-translate-x-2 group-focus-within:opacity-0">
        <Search/>
        Search
      </label>
      <input id="search" type="text"
             class="absolute md:relative w-full h-12 outline-none px-8"
             v-model="query"
             @input="onInput"
             @blur="onBlur"
             @focus="onInput"/>
    </div>

    <!-- Dropdown -->
    <Transition name="dropdown">
      <div v-if="showResults && results.length > 0"
           class="absolute top-full mt-2 left-0 w-96 z-50 bg-white
              border border-gray-200 rounded-2xl overflow-hidden shadow-lg">
        <div v-for="result in results"
             :key="result.id"
             class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50
                transition border-b border-gray-100 last:border-0 cursor-pointer"
             @mousedown.prevent="navigateToMessage(result)">
          <div class="min-w-0 flex flex-col flex-1">
            <span class="font-medium text-gray-900 truncate">{{ result.name }}</span>
            <span class="text-gray-400 text-xs truncate">{{ result.email }}</span>
            <span class="text-gray-500 text-xs truncate mt-0.5">{{ result.preview }}</span>
          </div>
        </div>

        <div v-if="results.length === 0"
             class="px-4 py-3 text-gray-400 text-sm text-center">
          No results for "{{ query }}"
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>