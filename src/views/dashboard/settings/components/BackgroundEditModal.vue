<script setup lang="ts">
import {ref} from 'vue'
import {X, Upload} from '@lucide/vue'
import type {Background} from "@views/dashboard/settings/components/Backgrounds.vue";

defineProps<{
  background: Background
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const ACCEPTED_TYPES: string[] = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = (): void => {
  fileInput.value?.click()
}

const onFileSelected = (event: Event): void => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (!ACCEPTED_TYPES.includes(file.type)) {
    input.value = ''
    return
  }

  // TODO: pass file to Cropper.js
  console.log('File selected:', file.name)
}
</script>


<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4 py-6"
         @click.self="emit('close')">
      <!-- Modal panel -->
      <div
          class="relative w-5/6 lg:w-2/3 xl:w-1/2 aspect-square bg-gray-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col">

        <!-- Background image -->
        <div class="absolute inset-0 z-0">
          <img :src="background.srcFull"
               :alt="background.label"
               class="w-full h-full object-cover"/>
        </div>

        <!-- Header -->
        <div class="relative z-10 flex items-center justify-between px-6 py-4 shrink-0">
          <div>
            <h3 class="text-xl font-unbounded font-semibold capitalize text-white"
                style="text-shadow: 0 0 10px rgba(0,0,0,1)">
              {{ background.label }}
            </h3>
            <p class="text-sm text-white/70 mt-0.5"
               style="text-shadow: 0 0 10px rgba(0,0,0,1)">
              Edit background image
            </p>
          </div>
          <button @click="emit('close')" class="p-2 rounded-full bg-black/30 hover:bg-white/50 transition text-white group">
            <X class="w-5 h-5 group-hover:scale-125 transition"/>
          </button>
        </div>

        <!-- Body -->
        <div class="relative z-10 flex-1 overflow-y-auto flex flex-col justify-center items-center">
          <!-- Modify button -->
          <div class="">
            <button @click="triggerFileInput"
                    class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/10 backdrop-blur-sm border
                    border-white/20 text-white font-semibold hover:bg-white/20 transition"
                    style="text-shadow: 0 0 10px rgba(0,0,0,1)">
              <Upload class="w-4 h-4"/>
              Modify image
            </button>
            <input ref="fileInput"
                   type="file"
                   accept=".jpg,.jpeg,.png,.gif,.webp"
                   class="hidden"
                   @change="onFileSelected"/>
          </div>
          <!-- TODO:  Crop (Cropper.js) -->
          <!-- TODO: Canvas processing + live preview -->
          <!-- TODO: Save -->
        </div>
        <!-- Footer -->
        <div class="relative z-10 flex justify-end gap-3 px-6 py-4 shrink-0">
          <button @click="emit('close')"
                  class="px-4 py-2 rounded-xl bg-black/30 backdrop-blur-sm border border-white/20
                   text-white hover:bg-black/50 transition font-medium">
            Cancel
          </button>
          <button :disabled="true"
                  class="px-4 py-2 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20
                  text-white font-semibold opacity-40 cursor-not-allowed transition">
            Save
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
