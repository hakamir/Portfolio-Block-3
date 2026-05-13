<script setup lang="ts">
import {type Gallery, useGalleriesStore} from "@stores/gallery.ts";
import {Ban, ChevronDown, GripVertical, LoaderCircle, MoreHorizontal, Plus, Save, Trash2} from "@lucide/vue";
import {v4 as uuidv4} from "uuid";
import {onMounted, onUnmounted, ref} from "vue";
import CollapseButton from "@views/dashboard/works/Components/CollapseButton.vue";
import DeleteButton from "@views/dashboard/works/Components/DeleteButton.vue";
import WorkInput from "@views/dashboard/works/Components/WorkInput.vue";
import CollapseTransition from "@components/CollapseTransition.vue";
import ImageInput from "@views/dashboard/works/Components/ImageInput.vue";
import {VueDraggable} from "vue-draggable-plus";
import {storeToRefs} from "pinia";

const galleriesStore = useGalleriesStore();
const isMobile = ref(false)

const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 768;
}

onMounted(async () => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  window.addEventListener('click', handleClickOutside)
  await galleriesStore.fetchGalleries()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  window.removeEventListener('click', handleClickOutside)
})

const openedMenu = ref<string | null>(null)

const toggleMenu = (key: string) => {
  openedMenu.value = openedMenu.value === key ? null : key
}

const handleClickOutside = () => {
  openedMenu.value = null
}

const addGallery = () => {
  galleriesStore.galleries.push({
    _id: '',
    title: '',
    slug: uuidv4(),
    order: galleriesStore.galleries.length + 1,
    images: []
  });
}

const addImage = (gallery: Gallery) => {
  const precise_date = new Date();
  precise_date.setUTCHours(0, 0, 0, 0);
  const date = precise_date.toISOString().split('.')[0];
  gallery.images.push({
    src: '',
    alt: '',
    title: '',
    location: '',
    date: date,
    order: gallery.images.length + 1,
  });
}

const deleteGallery = (gallery: Gallery) => {
  const index = galleriesStore.galleries.indexOf(gallery);
  galleriesStore.galleries.splice(index, 1);
}

const deleteImage = (gallery: Gallery, image: any) => {
  const index = gallery.images.indexOf(image);
  gallery.images.splice(index, 1);
}

const refreshKey = ref(0);
const {fetchStatus, uploadedFileName} = storeToRefs(galleriesStore);

const onSave = async () => {
  try {
    if (await galleriesStore.saveGalleries()) {
      await galleriesStore.fetchGalleries()
      refreshKey.value += 1;
    }
  } catch {
    console.error('Error saving images')
    fetchStatus.value = 'error'
  }
}

const collapsedGalleries = ref<Set<string>>(new Set());
const collapsedImages = ref<Set<string>>(new Set());

const toggleGalleryCollapse = (slug: string) => {
  collapsedGalleries.value.has(slug) ? collapsedGalleries.value.delete(slug) : collapsedGalleries.value.add(slug);
}
const toggleImageCollapse = (src: string) => {
  collapsedImages.value.has(src) ? collapsedImages.value.delete(src) : collapsedImages.value.add(src);
}

const reorderGalleries = () => {
  galleriesStore.galleries.forEach((gallery, index) => {
    gallery.order = index + 1;
  })
}

const reorderImages = (gallery: Gallery) => {
  gallery.images.forEach((image, index) => {
    image.order = index + 1;
  })
}

</script>

<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl md:p-6 flex flex-col">
    <div class="flex justify-between items-center md:mb-4 px-6 pt-4 md:p-0">
      <h2 class="text-2xl font-semibold mb-4">Galleries</h2>
      <button
          @click="addGallery"
          class="px-2 py-1 rounded-xl text-sm text-blue-600 hover:bg-blue-100 self-start transition flex justify-center items-center gap-2">
        <Plus/>
        New gallery
      </button>
    </div>

    <!-- DESKTOP -->
    <div v-if="!isMobile">
      <VueDraggable
          v-model="galleriesStore.galleries"
          handle=".drag-handle"
          group="galleries"
          @update="reorderGalleries()"
          class="flex flex-col gap-2">
        <div v-for="gallery in galleriesStore.galleries" :key="refreshKey">
          <div class="flex items-center justify-between">
            <div class="flex grow items-center">
              <!-- Collapse button -->
              <CollapseButton :collapsed="collapsedGalleries.has(gallery.slug)"
                              @toggle="toggleGalleryCollapse(gallery.slug)"
                              color="bg-primary-300/30"/>
              <!-- Gallery input -->
              <WorkInput label="Gallery" v-model="gallery.title" labelColor="bg-primary-300/30"
                         inputColor="focus:bg-primary-200/20"/>
            </div>
            <button
                @click="addImage(gallery)"
                class="work-add-album-btn group">
              <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
              <span
                  class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New image</span>
            </button>
            <!-- Delete gallery button -->
            <DeleteButton @delete="deleteGallery(gallery)" customClass="rounded-r-full" assignedFor="artist"/>
          </div>
          <CollapseTransition :show="!collapsedGalleries.has(gallery.slug)" customClass="flex">
            <div class="w-2 bg-primary-200/30 border-x border-b border-gray-400/30 mx-4 mb-1 rounded-b-full"/>
            <div class="flex flex-col grow">
              <VueDraggable
                  v-model="gallery.images"
                  handle=".drag-handle"
                  group="images"
                  @update="reorderImages(gallery)"
                  class="flex flex-col">
                <div v-for="image in gallery.images">
                  <div class="flex items-center mt-2">
                    <!-- Collapse button -->
                    <CollapseButton :collapsed="collapsedImages.has(image.src)"
                                    @toggle="toggleImageCollapse(image.src)"
                                    color="bg-yellow-300/30"/>
                    <!-- Image input -->
                    <WorkInput label="Image" v-model="image.title" labelColor="bg-yellow-300/30"
                               inputColor="focus:bg-yellow-200/20"/>
                    <!-- Delete image button -->
                    <DeleteButton @delete="deleteImage(gallery, image)" customClass="rounded-r-full"
                                  assignedFor="album"/>
                  </div>
                  <CollapseTransition :show="!collapsedImages.has(image.src)" customClass="flex" :delay="100">
                    <ImageInput :image="image" :gallerySlug="gallery.slug"/>
                  </CollapseTransition>
                </div>
              </VueDraggable>
            </div>
          </CollapseTransition>
        </div>
      </VueDraggable>
      <div class="flex justify-end items-center mt-4 gap-4">
        <div v-if="fetchStatus == 'error'" class="flex items-center gap-2 text-red-800 bg-red-100 rounded-full p-2">
          <Ban/>
          <span class="text-sm font-semibold">Error</span>
        </div>
        <button v-if="fetchStatus == 'idle' || fetchStatus == 'error'" @click="onSave"
                class="px-6 py-2 bg-blue-500 text-white rounded-2xl hover:bg-blue-600 transition flex items-center gap-2">
          <Save class="w-6 h-6"/>
          <span class="font-unbounded">Save</span>
        </button>
        <button v-if="fetchStatus == 'loading'" @click="onSave"
                class="px-6 py-2 bg-gray-700 text-white rounded-2xl transition flex items-center gap-2 cursor-not-allowed!">
          <LoaderCircle class="animate-spin"/>
          <span class="font-unbounded">Uploading: </span>
          <span class="text-blue-400 italic">{{ uploadedFileName }}</span>
        </button>
      </div>
    </div>

    <!-- MOBILE -->
    <div v-else class="flex flex-col">
      <VueDraggable v-model="galleriesStore.galleries"
                    handle=".drag-handle"
                    group="galleries"
                    @update="reorderGalleries()"
                    class="flex flex-col">
        <!-- GALLERIES -->
        <div v-for="(gallery, galleryIndex) in galleriesStore.galleries" :key="refreshKey">
          <div
              class="flex items-center outline-none bg-primary-500/20 hover:bg-primary-500/30 border border-primary-900/20 transition py-3 px-1">
            <label class="drag-handle">
              <GripVertical class="text-gray-400 mx-1"/>
            </label>
            <input
                class="w-full focus:bg-white border transition-all duration-300 border-transparent focus:border-gray-300 rounded-md px-2 py-1 mr-2 outline-none"
                v-model="gallery.title"
                type="text" placeholder="Gallery name"/>
            <div class="flex items-center gap-2">
              <button @click="toggleGalleryCollapse(gallery.slug)">
                <ChevronDown
                    class="transition-transform duration-200 p-1 w-8 h-8 border border-gray-300 rounded-full"
                    :class="collapsedGalleries.has(gallery.slug) ? 'rotate-180 bg-white text-black' : 'bg-white/50 text-gray-400'"/>
              </button>
              <div class="relative">
                <button
                    @click.stop="toggleMenu(`gallery-${galleryIndex}`)"
                    class="bg-white/50 transition p-1 w-8 h-8 border border-gray-300 rounded-full flex items-center justify-center hover:bg-white">
                  <MoreHorizontal class="w-4 h-4 text-gray-600"/>
                </button>
                <div v-if="openedMenu === `gallery-${galleryIndex}`"
                     class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden z-50">
                  <button
                      @click.stop="deleteGallery(gallery)"
                      class="w-full px-4 py-3 text-left text-red-600 hover:bg-red-50 transition">
                    <Trash2 class="inline-block mr-2 w-5 h-5"/>
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
          <CollapseTransition :show="collapsedGalleries.has(gallery.slug)" class="flex flex-col">
            <!-- New image button -->
            <button
                @click="addImage(gallery)"
                class="work-add-album-btn group flex items-center justify-center gap-2 px-4 py-2">
              <Plus class="text-blue-400 group-hover:text-blue-600 group-hover:scale-120 transition"/>
              <span
                  class="text-sm text-blue-600 group-hover:text-blue-700 group-hover:translate-x-1 transition">New image</span>
            </button>
            <!-- IMAGES -->
            <VueDraggable v-model="gallery.images"
                          handle=".drag-handle"
                          group="images"
                          @update="reorderImages(gallery)"
                          class="flex flex-col">
              <div v-for="(image, imageIndex) in gallery.images">
                <div
                    class="flex w-full outline-none bg-yellow-500/20 hover:bg-yellow-500/30 border border-yellow-900/20 transition py-3 px-1">
                  <label class="drag-handle">
                    <GripVertical class="text-gray-400"/>
                  </label>
                  <input class="w-full bg-white border border-gray-300 rounded-md px-2 py-1"
                         v-model="image.title"
                         type="text" placeholder="Image title"/>
                  <button @click="toggleImageCollapse(`image-m-${galleryIndex}-${imageIndex}`)" class="px-2">
                    <ChevronDown
                        class="transition-transform duration-200 p-1 w-8 h-8 border border-gray-300 rounded-full flex items-center justify-center"
                        :class="collapsedImages.has(`image-m-${galleryIndex}-${imageIndex}`) ? 'rotate-180 bg-white text-black' : 'bg-white/50 text-gray-400'"/>
                  </button>
                  <div class="relative">
                    <button
                        @click.stop="toggleMenu(`image-${galleryIndex}-${imageIndex}`)"
                        class="bg-white/50 transition p-1 w-8 h-8 border border-gray-300 rounded-full flex items-center justify-center hover:bg-white">
                      <MoreHorizontal class="w-4 h-4 text-gray-600"/>
                    </button>
                    <div v-if="openedMenu === `image-${galleryIndex}-${imageIndex}`"
                         class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-xl shadow-lg z-50">
                      <button
                          @click.stop="deleteImage(gallery, image)"
                          class="w-full px-4 py-3 text-left text-red-600 hover:bg-red-50 transition">
                        <Trash2 class="inline-block mr-2 w-5 h-5"/>
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
                <CollapseTransition :show="collapsedImages.has(`image-m-${galleryIndex}-${imageIndex}`)"
                                    class="flex flex-col">
                  <ImageInput :image="image" :gallerySlug="gallery.slug" :isMobile="true"/>
                </CollapseTransition>
              </div>
            </VueDraggable>
          </CollapseTransition>
        </div>
      </VueDraggable>
      <div class="flex items-center">
        <div v-if="fetchStatus == 'error'" class="flex items-center gap-2 text-red-800 bg-red-100 rounded-full p-2">
          <Ban/>
          <span class="text-sm font-semibold">An error occurred. Some files may not have been uploaded.</span>
        </div>
        <button v-if="fetchStatus == 'idle' || fetchStatus == 'error'" @click="onSave"
                class="px-6 py-4 w-full bg-black text-white rounded-b-xl transition flex items-center justify-center gap-2">
          <Save class="w-6 h-6"/>
          <span class="font-unbounded">Save</span>
        </button>
        <button v-if="fetchStatus == 'loading'" @click="onSave"
                class="px-6 py-4 w-full bg-gray-700 text-white rounded-b-xl transition flex items-center justify-center gap-2 cursor-not-allowed!">
          <LoaderCircle class="animate-spin"/>
          <span class="font-unbounded">Uploading...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
