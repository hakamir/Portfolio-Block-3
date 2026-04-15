<script setup lang="ts">
import {Mails, UserRoundPen, BriefcaseBusiness, Settings } from "@lucide/vue";
</script>

<template>
  <div class="mt-36 container mx-auto flex gap-6 border-b-2 border-gray-200">
    <RouterLink :to="{name: 'dashboard-messages'}" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <Mails />
      <span class="font-bold font-unbounded">Messages</span>
    </RouterLink>
    <RouterLink :to="{name: 'dashboard-biography'}" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <UserRoundPen />
      <span class="font-bold font-unbounded">Biography</span>
    </RouterLink>
    <RouterLink :to="{name: 'dashboard-works'}" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <BriefcaseBusiness  />
      <span class="font-bold font-unbounded">Works</span>
    </RouterLink>
    <RouterLink :to="{name: 'dashboard-settings'}" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <Settings  />
      <span class="font-bold font-unbounded">Settings</span>
    </RouterLink>
  </div>
</template>

<style scoped>

</style>