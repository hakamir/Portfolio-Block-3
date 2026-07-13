<script setup lang="ts">
import {nextTick, onBeforeUnmount, ref} from 'vue'
import {X, Upload, CropIcon, CircleX} from '@lucide/vue'
import type {Background} from "@views/dashboard/settings/components/Backgrounds.vue";
import Cropper from 'cropperjs'
import Modal from "@/components/Modal.vue";
import {instance} from "@api/axios.ts";
import uploadApi from "@api/upload.ts";
import axios from "axios";

const props = defineProps<{
  background: Background
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', destination: string): void
}>()

interface PreviewItem {
  size: number // Image size in pixels (square)
  canvas: HTMLCanvasElement
  quality: number // Compression quality (0-100)
  blobUrl: string | null // Blob URL for the preview image (temporarily stored)
  fileSize: number | null
}

const ACCEPTED_TYPES: string[] = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

const fileInput = ref<HTMLInputElement | null>(null)
const cropperImageElement = ref<HTMLImageElement | null>(null)
const cropperInstance = ref<Cropper | null>(null)
const imageObjectUrl = ref<string | null>(null)
const showConfirmModal = ref(false)
const isSaving = ref(false)
const saveError = ref<string | null>(null)
type Step = 'idle' | 'crop' | 'preview'
const step = ref<Step>('idle')
const croppedCanvases = ref<{ size: number, canvas: HTMLCanvasElement } []>([])

const triggerFileInput = (): void => {
  fileInput.value?.click()
}

const onFileSelected = async (event: Event): Promise<void> => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (!ACCEPTED_TYPES.includes(file.type)) {
    input.value = ''
    return
  }

  // Revoke previous URL to avoid memory leak
  if (imageObjectUrl.value) URL.revokeObjectURL(imageObjectUrl.value)
  imageObjectUrl.value = URL.createObjectURL(file)

  step.value = 'crop'
  // Wait for the <img> to appear in the DOM
  await nextTick()
  initCropper()
}

const initCropper = (): void => {
  if (!cropperImageElement.value) return

  // Remove cropper instance if it exists
  cropperInstance.value?.destroy()

  // Instantiate cropper with custom template - Replace the img element with a cropper canvas
  cropperInstance.value = new Cropper(cropperImageElement.value, {
    template: `
      <cropper-canvas background class="w-full h-full" >
        <cropper-image rotatable translatable></cropper-image>
        <cropper-shade hidden></cropper-shade>
        <cropper-handle action="select" plain></cropper-handle>
        <cropper-selection id="cropper-selection" initial-coverage="0.5" movable resizable aspect-ratio="1">
          <cropper-grid role="grid" bordered covered></cropper-grid>
          <cropper-handle action="move" theme-color="rgba(255,255,255,0.35)"></cropper-handle>
          <cropper-handle action="ne-resize"></cropper-handle>
          <cropper-handle action="nw-resize"></cropper-handle>
          <cropper-handle action="se-resize"></cropper-handle>
          <cropper-handle action="sw-resize"></cropper-handle>
        </cropper-selection>
      </cropper-canvas>
    `
  })

  // Get references to the selection and canvas elements
  const selection = cropperInstance.value?.getCropperSelection()
  const canvas = cropperInstance.value?.getCropperCanvas()
  if (!selection || !canvas) return

  // Flag set to bypass the boundary check while the initial-coverage is applied
  let isInitializing = true

  // Set "initial-coverage" to cover the most of the image (width or height)
  // Timeout is needed to allow the initial-coverage to be applied after the canvas is fully rendered
  setTimeout(() => {
    const cropperImage = cropperInstance.value?.getCropperImage()
    if (!cropperImage) return

    const canvasRect = (canvas as HTMLElement).getBoundingClientRect()
    const imageRect = (cropperImage as HTMLElement).getBoundingClientRect()

    // Get the largest dimension of the image (- 1 to avoid rounding errors that could block the selection)
    const size = Math.min(imageRect.width, imageRect.height) - 1

    // Center the selection on the image within the canvas coordinates space
    const x = (imageRect.left - canvasRect.left) + (imageRect.width - size) / 2
    const y = (imageRect.top - canvasRect.top) + (imageRect.height - size) / 2

    // Apply the position and size to the selection
    selection.$change(x, y, size, size)

    // Boundary check is allowed now
    isInitializing = false
  }, 200)

  // Bound selection to the image bounds - prevent selection outside the image
  selection.addEventListener('change', (event: Event) => {
    if (isInitializing) return  // skip boundary check during init

    const e = event as CustomEvent
    const canvasRect = canvas.getBoundingClientRect()
    const cropperImage = cropperInstance.value?.getCropperImage()
    if (!cropperImage) return

    // Get the bounding box of the image
    const imageRect = cropperImage.getBoundingClientRect()

    // Define the maximum selection bounds based on the image dimensions
    const maxSelection = {
      x: imageRect.left - canvasRect.left,
      y: imageRect.top - canvasRect.top,
      width: imageRect.width,
      height: imageRect.height,
    }

    // e.detail from CustomEvent contains x, y, width, height from the selection
    const sel = e.detail

    // Calculate if the selection is inside the image bounds
    const isInside =
        sel.x >= maxSelection.x &&
        sel.y >= maxSelection.y &&
        sel.x + sel.width <= maxSelection.x + maxSelection.width &&
        sel.y + sel.height <= maxSelection.y + maxSelection.height

    // Cancel change if the selection is outside the image bounds
    if (!isInside) event.preventDefault()
  })
}

// Resize a canvas to a square target resolution
const resizeCanvas = (source: HTMLCanvasElement, targetSize: number): HTMLCanvasElement => {
  // Create the destination canvas with the target size
  const output = document.createElement('canvas')
  output.width = targetSize
  output.height = targetSize

  // Draw and scale the source canvas to the destination canvas
  // The browser will automatically handle the scaling
  output.getContext('2d')!.drawImage(source, 0, 0, targetSize, targetSize)

  return output
}

// Validate the crop selection and generate the preview images (res: 2048, 1024, 512)
const validateCrop = async (): Promise<void> => {
  // Get the selection
  const selection = cropperInstance.value?.getCropperSelection()
  if (!selection) return

  // Convert the selection to a canvas
  const canvas2048 = await selection.$toCanvas({width: 2048, height: 2048})
  if (!canvas2048) return

  // Resize the canvas
  const canvas1024 = resizeCanvas(canvas2048, 1024)
  // Use canvas1024 to reduce aliasing artifacts provoked by brutal resizing (smaller step = less aliasing)
  const canvas512 = resizeCanvas(canvas1024, 512)

  // Store the cropped canvases in the state
  croppedCanvases.value = [
    {size: 2048, canvas: canvas2048},
    {size: 1024, canvas: canvas1024},
    {size: 512, canvas: canvas512},
  ]

  // Next step: Generate the preview images
  await initPreviews(croppedCanvases.value)
  step.value = 'preview'
}

const previews = ref<PreviewItem[]>([]) // Store the preview images data
const previewIndex = ref(0) // Used to track the current preview index (2048, 1024, 512)


// Build preview images for each canvas with default quality (85%)
const initPreviews = async (canvases: { size: number, canvas: HTMLCanvasElement }[]): Promise<void> => {
  // "quality" linked to the slider value via v-model
  previews.value = canvases.map(({size, canvas}) => ({
    size,
    canvas,
    quality: 85,
    blobUrl: null,
    fileSize: null,
  }))
  await generateAllPreviews()
}

// Call on slider "quality" changes to update the preview image quality
const generatePreview = async (index: number): Promise<void> => {
  const item = previews.value[index]
  if (!item) return

  // Revoke previous blob URL
  if (item.blobUrl) URL.revokeObjectURL(item.blobUrl)

  // Execute the conversion to blob with the new quality
  const blob = await blobFromCanvas(item.canvas, {quality: item.quality})

  // Create a new blob URL
  item.blobUrl = URL.createObjectURL(blob)

  // Retrieve file size from the blob
  item.fileSize = blob.size
}

// Generate all preview images on initial load (default quality 85%)
const generateAllPreviews = async (): Promise<void> => {
  await Promise.all(previews.value.map((_, i) => generatePreview(i)))
}

// Convert canvas to blob with applied quality
const blobFromCanvas = (canvas: HTMLCanvasElement, {type = 'image/webp', quality = 85}: {
  type?: string,
  quality?: number
} = {}): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob)
      else reject(new Error('Failed to generate blob'))
    }, type, quality / 100)
  })
}

// Generate the resized preview images and upload them to the server
const save = async (): Promise<void> => {
  saveError.value = null
  // Lock the UI during the upload process
  isSaving.value = true
  showConfirmModal.value = false

  try {
    // Get three preview images
    const [item2048, item1024, item512] = previews.value

    // Convert each preview image to compressed webp blobs (parallel operation)
    const [blob2048, blob1024, blob512] = await Promise.all([
      blobFromCanvas(item2048.canvas, {quality: item2048.quality}),
      blobFromCanvas(item1024.canvas, {quality: item1024.quality}),
      blobFromCanvas(item512.canvas, {quality: item512.quality}),
    ])

    // Build a form data object and append the three blobs and the destination (hero, portfolio, etc.)
    const formData = new FormData()
    formData.append('image-2048', blob2048)
    formData.append('image-1024', blob1024)
    formData.append('image-512', blob512)
    formData.append('destination', props.background.destination)

    // Upload the form data to the server
    await instance.post(uploadApi.uploadBackground, formData)

    // Signal to the parent component that the background has been saved
    emit('save', props.background.destination)

    // Close the modal
    emit('close')

  } catch (e) {
    saveError.value = 'Failed to save background. '
    if (axios.isAxiosError(e)) {
      saveError.value += e.response ? `Status: ${e.response.status}` : ''
    }
  } finally {
    isSaving.value = false
  }
}

onBeforeUnmount(() => {
  cropperInstance.value?.destroy()
  if (imageObjectUrl.value) URL.revokeObjectURL(imageObjectUrl.value)
})
</script>


<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4 py-6">
      <!-- Modal panel -->
      <div
          class="relative w-5/6 lg:w-2/3 xl:w-1/2 aspect-square bg-gray-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col">

        <!-- Background image -->
        <div v-if="!imageObjectUrl" class="absolute inset-0 z-0">
          <img :src="background.srcFull"
               :alt="background.label"
               class="w-full h-full object-cover"/>
        </div>

        <!-- Header -->
        <div class="relative z-10 flex items-center justify-between px-6 py-4 shrink-0">
          <div>
            <h3 class="text-xl font-unbounded font-semibold text-white text-shadow-[0_0_10px_rgba(0,0,0,1)]">
              {{ background.label.toUpperCase() }} SECTION
            </h3>
            <div class="text-sm text-white/70 mt-0.5 text-shadow-[0_0_10px_rgba(0,0,0,1)]">
              <div v-if="step === 'idle'">
                <h4 class="font-semibold text-lg">Current background</h4>
              </div>
              <div v-else-if="step === 'crop'">
                <h4 class="font-semibold text-lg">Crop image</h4>
              </div>
              <div v-else-if="step === 'preview'">
                <h4 class="font-semibold text-lg">Preview image</h4>
              </div>
            </div>
          </div>
          <div v-if="saveError" class="flex items-center gap-2 text-red-400 bg-red-600/20 px-2 py-1 rounded-full text-sm">
            <CircleX/>
            <span class="font-semibold">{{ saveError }}</span>
          </div>
          <button @click="emit('close')"
                  class="p-2 rounded-full bg-black/30 hover:bg-white/50 transition text-white group">
            <X class="w-5 h-5 group-hover:scale-125 transition"/>
          </button>
        </div>

        <!-- Body -->
        <div class="relative z-10 flex-1 flex flex-col justify-center items-center">

          <!-- IDLE: Modify button -->
          <div v-if="step === 'idle'">
            <button @click="triggerFileInput"
                    class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-black/50 backdrop-blur-sm border group
            border-white/20 text-white font-semibold hover:bg-black/70 transition shadow-[0_0_10px_rgba(0,0,0,1)]">
              <Upload class="w-4 h-4 group-hover:animate-pulse group-hover:scale-125 transition"/>
              Modify image
            </button>
            <input ref="fileInput"
                   type="file"
                   accept=".jpg,.jpeg,.png,.gif,.webp"
                   class="hidden"
                   @change="onFileSelected"/>
          </div>

          <!-- CROP: Crop image with ratio 1:1 -->
          <div v-else-if="step === 'crop'" class="w-full h-full">
            <img ref="cropperImageElement"
                 alt="Background Image Cropper"
                 :src="imageObjectUrl!"
                 class="block max-w-full"/>
          </div>

          <!-- PREVIEW: Set quality -->
          <div v-else-if="step === 'preview'" class="absolute inset-0 flex flex-col">

            <!-- Image -->
            <div class="flex-1 min-h-0 overflow-hidden flex items-center justify-center bg-black/20">
              <img v-if="previews[previewIndex].blobUrl"
                   :src="previews[previewIndex].blobUrl!"
                   :alt="`Preview ${previews[previewIndex].size}px`"
                   class="max-w-full max-h-full object-contain"/>
            </div>

            <!-- Slider + info -->
            <div class="shrink-0 px-6 py-3 flex items-center gap-4 bg-black/30 backdrop-blur-sm">
              <span class="text-white font-unbounded font-semibold w-20 shrink-0">
                Quality
              </span>
              <input type="range" min="1" max="100"
                     v-model.number="previews[previewIndex].quality"
                     @change="generatePreview(previewIndex)"
                     class="flex-1 accent-white"/>
              <span class="text-white/60 text-xs w-12 text-right shrink-0">
      {{ previews[previewIndex].quality }}
    </span>
              <span class="text-white/40 text-xs w-20 text-right shrink-0">
      {{ previews[previewIndex].fileSize ? (previews[previewIndex].fileSize! / 1024).toFixed(1) + ' KB' : '—' }}
    </span>
            </div>

          </div>

        </div>
        <!-- Footer -->
        <div class="flex items-center justify-between">
          <!-- Image selection indicator -->
          <div v-if="step === 'idle'" class="flex flex-col px-6 py-4 select-none z-10">
            <span
                class="text-white font-semibold bg-black/50 px-3 py-1 rounded-t-2xl">Select a new background image. </span>
            <span class="text-gray-300 bg-black/50 px-3 py-1 rounded-b-2xl ">It is preferred to use an image in high resolution. (Recommended resolution: 2048x2048 or higher)</span>
          </div>

          <!-- Crop indicator -->
          <div v-if="step === 'crop'" class="flex flex-col px-6 py-4 select-none z-10">
            <span
                class="text-white font-semibold bg-black/50 px-3 py-1 rounded-t-2xl">Select the region to crop. </span>
            <span class="text-gray-300 bg-black/50 px-3 py-1 rounded-b-2xl ">Aspect ratio is forced to 1:1. The higher the selection, the detailed the image will be.</span>
          </div>

          <!-- Preview indicator (2048, 1024, 512) -->
          <div v-if="step === 'preview'" class="flex items-center gap-6 px-6 py-4 select-none">
            <span class="font-unbounded"
                  :class="previewIndex === 0 ? 'text-white scale-120 transition' : 'text-white/40'">2048</span>
            <span class="text-white/40 font-thin">—</span>
            <span class="font-unbounded"
                  :class="previewIndex === 1 ? 'text-white scale-120 transition' : 'text-white/40'">1024</span>
            <span class="text-white/40 font-thin">—</span>
            <span class="font-unbounded"
                  :class="previewIndex === 2 ? 'text-white scale-120 transition' : 'text-white/40'">512</span>
            <div class="flex flex-col">
              <span class="text-gray-300 bg-black/50 px-3 py-1 rounded-t-2xl">Select the best compression level for each resolution.</span>
              <span class="text-gray-500 bg-black/50 px-3 text-sm py-1 rounded-b-2xl">100% is the highest quality, but also the largest file size and has impact on performance.</span>
            </div>
          </div>

          <div class="relative z-10 flex gap-3 px-6 py-4">
            <!-- Cancel button -->
            <button @click="emit('close')"
                    class="px-4 py-2 rounded-xl bg-black/30 backdrop-blur-sm border border-white/20
                  text-white hover:bg-black/50 transition font-medium">
              Cancel
            </button>

            <!-- Back button (preview only - disabled for 2048) -->
            <button v-if="step === 'preview'" @click="previewIndex--"
                    class="px-4 py-2 rounded-xl bg-black/30 backdrop-blur-sm border border-white/20
                  text-white hover:bg-black/50 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed!"
                    :disabled="previewIndex === 0">
              Back
            </button>

            <!-- Validate crop -->
            <button v-if="step === 'crop'" @click="validateCrop"
                    class="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-gray-900 font-semibold hover:bg-gray-100 transition">
              <CropIcon class="w-4 h-4"/>
              Validate
            </button>

            <!-- Next (2048 and 1024) -->
            <button v-if="step === 'preview' && previewIndex < 2"
                    @click="previewIndex++"
                    class="px-4 py-2 rounded-xl bg-white text-gray-900 font-semibold hover:bg-gray-100 transition">
              Next
            </button>

            <!-- Save (512 only) -->
            <button v-if="step === 'preview' && previewIndex === 2" @click="showConfirmModal = true"
                    :disabled="isSaving"
                    class="px-4 py-2 rounded-xl bg-white text-gray-900 font-semibold hover:bg-gray-100 transition
                          disabled:opacity-50 disabled:cursor-not-allowed!">
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- Confirm modal -->
    <Modal v-if="showConfirmModal"
           :close-on-backdrop="true"
           :buttons="[
         { label: 'Cancel', color: 'white', action: () => showConfirmModal = false },
         { label: 'Confirm', color: 'red', action: save },
       ]"
           @close="showConfirmModal = false">
      <template #header>Save background</template>
      ⚠️ This will overwrite the current image. Are you sure?
    </Modal>
  </Teleport>
</template>