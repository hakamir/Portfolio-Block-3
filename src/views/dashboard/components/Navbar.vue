<script setup lang="ts">
import { computed } from "vue";
import { Mails, UserRoundPen, BriefcaseBusiness, Settings, ShieldCog } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import router from "@/router";

const auth = useAuthStore();

const items = [
  {
    routeName: "dashboard-messages",
    label: "Messages",
    icon: Mails,
  },
  {
    routeName: "dashboard-biography",
    label: "Biography",
    icon: UserRoundPen,
  },
  {
    routeName: "dashboard-works",
    label: "Works",
    icon: BriefcaseBusiness,
  },
  {
    routeName: "dashboard-admin",
    label: "Admin",
    icon: ShieldCog,
  },
  {
    routeName: "dashboard-settings",
    label: "Settings",
    icon: Settings,
  },
];

const visibleItems = computed(() =>
  items.filter(item => {
    const route = router.getRoutes().find(r => r.name === item.routeName);

    const roles = route?.meta.roles as string[] | undefined;

    return !roles || roles.includes(auth.payload?.role ?? "");
  })
);
</script>

<template>
  <div class="mt-36 container mx-auto flex gap-6 border-b-2 border-gray-200 justify-center">
    <RouterLink
      v-for="item in visibleItems"
      :key="item.routeName"
      :to="{ name: item.routeName }"
      active-class="text-blue-600 scale-115"
      class="flex items-center gap-2 hover:scale-105 hover:-translate-y-1 transition px-4 py-4"
    >
      <component :is="item.icon" />
      <span class="font-bold font-unbounded hidden md:inline">
        {{ item.label }}
      </span>
    </RouterLink>
  </div>
</template>

<style scoped>

</style>