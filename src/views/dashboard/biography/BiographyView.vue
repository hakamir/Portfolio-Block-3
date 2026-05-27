<script setup lang="ts">
import BiographyForm from "@views/dashboard/biography/components/BiographyForm.vue";
import {ref} from "vue";
import {onBeforeRouteLeave} from "vue-router";
import {useBiographyStore} from "@stores";
import Modal from "@components/Modal.vue";

const biographyStore = useBiographyStore()

const showUnsavedChangesModal = ref(false)
let resolveNavigation: ((confirm: boolean) => void) | null = null

onBeforeRouteLeave(() => {
  if (!biographyStore.isDirty) return true
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

</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-4 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded">Biography</h1>
    <BiographyForm/>
  </section>
  <Modal v-if="showUnsavedChangesModal"
         :buttons="[{ label: 'Stay', color: 'blue', action: onCancelLeave },
                  { label: 'Leave anyway', color: 'white', action: onConfirmLeave }]"
         @close="onCancelLeave" :closeOnBackdrop="true">
    <template #header>Unsaved changes</template>
    <p class="text-sm text-gray-800">You have unsaved changes. Are you sure you want to leave?</p>
  </Modal>
</template>

<style scoped>

</style>