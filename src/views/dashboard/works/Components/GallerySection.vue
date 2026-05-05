<script setup lang="ts">
import {type Gallery, useGalleriesStore} from "@stores/gallery.ts";
import {Ban, LoaderCircle, Plus, Save} from "@lucide/vue";
import {v4 as uuidv4} from "uuid";
import {onMounted, ref} from "vue";
import CollapseButton from "@views/dashboard/works/Components/CollapseButton.vue";
import DeleteButton from "@views/dashboard/works/Components/DeleteButton.vue";
import WorkInput from "@views/dashboard/works/Components/WorkInput.vue";
import CollapseTransition from "@components/CollapseTransition.vue";
import ImageInput from "@views/dashboard/works/Components/ImageInput.vue";
import {VueDraggable} from "vue-draggable-plus";
import {storeToRefs} from "pinia";

const galleriesStore = useGalleriesStore();

onMounted(async () => {
  await galleriesStore.fetchGalleries()
})

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
  precise_date.setUTCHours(0,0,0,0);
  const date = precise_date.toISOString().split('.')[0];
  gallery.images.push({
    src: '',
    alt: '',
    title: '',
    location: '',
    date:  date,
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
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6 flex flex-col">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-semibold mb-4">Galleries</h2>
      <button
          @click="addGallery"
          class="px-2 py-1 rounded-xl text-sm text-blue-600 hover:bg-blue-100 self-start transition flex justify-center items-center gap-2">
        <Plus/>
        New gallery
      </button>
    </div>
    <!-- GALLERIES -->
    <VueDraggable
        v-model="galleriesStore.galleries"
        handle=".drag-handle"
        group="artists"
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
                group="tracks"
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
        <Ban />
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
        <span class="text-blue-400 italic">{{uploadedFileName}}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>

</style>