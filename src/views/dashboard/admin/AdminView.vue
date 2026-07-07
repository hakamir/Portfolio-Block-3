<script setup lang="ts">

import UserView from "@views/dashboard/admin/components/UserView.vue";
</script>

<template>
  <section class="pt-8 pb-16 md:pt-16 container mx-auto px-4 md:px-32">
    <h1 class="text-4xl font-bold font-unbounded mb-8">Admin</h1>
    <div class="flex flex-col gap-8">
      <!-- Children components go here -->
      <UserView />
    </div>
  </section>
</template>

<style scoped>

</style>