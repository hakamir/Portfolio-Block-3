<script setup lang="ts">
import {Mails, UserRoundPen, BriefcaseBusiness, Settings } from "@lucide/vue";
</script>

<template>
  <div class="mt-36 container mx-auto flex gap-6 border-b-2 md:scale-100 border-gray-200 justify-center">
    <RouterLink :to="{name: 'dashboard-messages'}" active-class="text-blue-600 scale-115" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <Mails />
      <span class="font-bold font-unbounded hidden md:inline">Messages</span>
    </RouterLink>
    <RouterLink :to="{name: 'dashboard-biography'}" active-class="text-blue-600 scale-115" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <UserRoundPen />
      <span class="font-bold font-unbounded hidden md:inline">Biography</span>
    </RouterLink>
    <RouterLink :to="{name: 'dashboard-works'}" active-class="text-blue-600 scale-115" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <BriefcaseBusiness  />
      <span class="font-bold font-unbounded hidden md:inline">Works</span>
    </RouterLink>
    <RouterLink :to="{name: 'dashboard-settings'}" active-class="text-blue-600 scale-115" class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4">
      <Settings  />
      <span class="font-bold font-unbounded hidden md:inline">Settings</span>
    </RouterLink>
  </div>
</template>

<style scoped>

</style>