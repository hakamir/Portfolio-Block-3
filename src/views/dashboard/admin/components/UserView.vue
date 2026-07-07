<script setup lang="ts">
import {computed, onMounted, ref} from "vue";
import {useUserStore} from "@/stores/user";
import {useAuthStore} from "@/stores/auth";
import type {User} from "@/stores/user";
import Modal from "@components/Modal.vue";
import {PackageOpen, ShieldCheck, Trash2, UserPlus, Zap, TriangleAlert} from "@lucide/vue";
import Tooltip from "@components/layout/Tooltip.vue";

const userStore = useUserStore();
const authStore = useAuthStore();

const isSelf = (user: User) => user.id === authStore.payload?.sub;

const showCreateModal = ref(false);
const createForm = ref({email: "", password: "", passwordConfirm: "", role: "artist"});
const createError = ref<string | null>(null);

const showDeleteModal = ref(false);
const userToDelete = ref<User | null>(null);

const showRoleModal = ref(false);
const userToChangeRole = ref<User | null>(null);
const pendingRole = computed(() =>
    userToChangeRole.value?.role === "artist" ? "admin" : "artist"
);

const showActivateModal = ref(false);
const userToActivate = ref<User | null>(null);
const activeArtist = computed(() =>
    userStore.users?.find(u => u.role === "artist" && u.is_active) ?? null
);

const openCreateModal = () => {
  createForm.value = {email: "", password: "", passwordConfirm: "", role: "artist"};
  createError.value = null;
  showCreateModal.value = true;
};

const onConfirmCreate = async () => {
  if (createForm.value.password !== createForm.value.passwordConfirm) {
    createError.value = "Passwords do not match.";
    return;
  }
  if (userStore.users?.some(u => u.email === createForm.value.email)) {
    createError.value = "This email is already in use.";
    return;
  }
  try {
    await userStore.createUser(createForm.value.email, createForm.value.password, createForm.value.role);
    showCreateModal.value = false;
  } catch (e: any) {
    createError.value = e.response?.data?.error ?? "An error occurred. Please try again.";
  }
};

const openDeleteModal = (user: User) => {
  userToDelete.value = user;
  showDeleteModal.value = true;
};

const onConfirmDelete = async () => {
  if (!userToDelete.value) return;
  await userStore.deleteUser(userToDelete.value.id);
  showDeleteModal.value = false;
  userToDelete.value = null;
};

const openRoleModal = (user: User) => {
  userToChangeRole.value = user;
  showRoleModal.value = true;
};

const onConfirmChangeRole = async () => {
  if (!userToChangeRole.value) return;
  await userStore.changeUserRole(userToChangeRole.value.id, pendingRole.value);
  showRoleModal.value = false;
  userToChangeRole.value = null;
};

const openActivateModal = (user: User) => {
  userToActivate.value = user;
  showActivateModal.value = true;
};

const onConfirmActivate = async () => {
  if (!userToActivate.value) return;
  await userStore.activateUser(userToActivate.value.id);
  showActivateModal.value = false;
  userToActivate.value = null;
};

onMounted(() => {
  userStore.getUsers();
});
</script>

<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">

    <!-- Header -->
    <div class="mb-6 flex justify-between items-start">
      <div>
        <h2 class="text-2xl font-unbounded font-semibold">Users</h2>
        <p class="text-sm text-gray-500 mt-1">All users in the system.</p>
      </div>
      <button
          @click="openCreateModal"
          class="flex items-center gap-2 bg-lime-600 hover:bg-lime-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition">
        <UserPlus class="w-4 h-4"/>
        Add user
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="!userStore.users?.length" class="flex flex-col items-center justify-center py-8 gap-2">
      <PackageOpen class="w-10 h-10 text-gray-400"/>
      <span class="text-sm text-gray-500 font-unbounded">No users found...</span>
    </div>

    <!-- Users list -->
    <div v-else class="border border-gray-200 rounded-xl overflow-hidden">
      <div
          v-for="user in userStore.users"
          :key="user.id"
          class="flex items-center gap-2 sm:gap-3 px-4 py-3 bg-white border-b border-gray-200 last:border-0 group hover:bg-gray-50 transition">

        <!-- Active dot -->
        <span class="w-4 h-4 rounded-full shrink-0"
              :class="[user.is_active ? 'bg-lime-500' : user.role === 'admin' ? 'bg-gray-300' : 'bg-orange-300']"/>

        <!-- Email + role badge (mobile only, shown below email) -->
        <div class="grow min-w-0">
          <span class="block text-sm text-gray-800 truncate group-hover:translate-x-1 transition">{{ user.email }}</span>
          <span
              class="sm:hidden inline-flex mt-0.5 text-xs font-semibold px-2 py-0.5 rounded-full border select-none"
              :class="user.role === 'admin'
                ? 'bg-lime-100 text-lime-800 border-lime-200'
                : 'bg-blue-100 text-blue-800 border-blue-200'">
            {{ user.role }}
          </span>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1 sm:w-28 justify-end shrink-0">

          <!-- Activate (inactive artists only) -->
          <Tooltip v-if="!isSelf(user) && user.role === 'artist' && !user.is_active" message="Set as active artist" side="bottom" :icon="Zap" iconBgColor="bg-lime-700/50">
            <button
                @click="openActivateModal(user)"
                class="p-2 rounded-full text-gray-400 hover:text-lime-600 hover:bg-lime-100 transition">
              <Zap class="w-6 h-6"/>
            </button>
          </Tooltip>

          <!-- Change role (hidden for self) -->
          <Tooltip v-if="!isSelf(user) && !user.is_active" message="Change role" side="bottom" :icon="ShieldCheck" iconBgColor="bg-blue-700/50">
            <button
                @click="openRoleModal(user)"
                class="p-2 rounded-full text-gray-400 hover:text-blue-600 hover:bg-blue-100 transition">
              <ShieldCheck class="w-6 h-6"/>
            </button>
          </Tooltip>

          <!-- Delete (blocked for active users and self) -->
          <Tooltip v-if="!isSelf(user) && !user.is_active" message="Delete user" side="bottom" :icon="Trash2" iconBgColor="bg-red-700/50">
            <button
                @click="openDeleteModal(user)"
                class="p-2 rounded-full text-gray-400 hover:text-red-600 hover:bg-red-100 transition">
              <Trash2 class="w-6 h-6"/>
            </button>
          </Tooltip>
        </div>

        <!-- "Your account" badge: desktop only -->
        <span v-if="isSelf(user)"
              class="hidden sm:inline-flex text-xs font-semibold px-2.5 py-1 rounded-full text-gray-100 bg-violet-700 select-none text-center shrink-0">
          Your account
        </span>

        <!-- Role badge: desktop only -->
        <span class="hidden sm:inline-flex text-xs font-semibold px-2.5 py-1 rounded-full border select-none w-14 text-center shrink-0"
              :class="user.role === 'admin'
                ? 'bg-lime-100 text-lime-800 border-lime-200'
                : 'bg-blue-100 text-blue-800 border-blue-200'">
          {{ user.role }}
        </span>

      </div>
    </div>
  </div>

  <!-- Create user modal -->
  <Modal
      v-if="showCreateModal"
      :icon="UserPlus"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showCreateModal = false },
        { label: 'Create', color: 'green', action: onConfirmCreate },
      ]"
      @close="showCreateModal = false">
    <template #header>New user</template>
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Email</label>
        <input
            v-model="createForm.email"
            type="email"
            placeholder="user@example.com"
            class="border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-lime-500"/>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Password</label>
        <input
            v-model="createForm.password"
            type="password"
            placeholder="••••••••"
            class="border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-lime-500"/>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Confirm password</label>
        <input
            v-model="createForm.passwordConfirm"
            type="password"
            placeholder="••••••••"
            class="border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-lime-500"/>
      </div>
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">Role</label>
        <select
            v-model="createForm.role"
            class="border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-lime-500">
          <option value="artist">Artist</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
      <TriangleAlert class="text-red-500 w-5 h-5"/>
      <span v-if="createError" class="text-sm! text-red-500">{{ createError }}</span>
        </div>
    </div>
  </Modal>

  <!-- Delete confirmation modal -->
  <Modal
      v-if="showDeleteModal"
      :icon="Trash2"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showDeleteModal = false },
        { label: 'Delete', color: 'red', action: onConfirmDelete },
      ]"
      @close="showDeleteModal = false">
    <template #header>Delete user</template>
    <p class="text-sm text-gray-600">
      Are you sure you want to delete
      <span class="font-semibold text-gray-800">{{ userToDelete?.email }}</span>?
      This action cannot be undone.
    </p>
  </Modal>

  <!-- Change role modal -->
  <Modal
      v-if="showRoleModal"
      :icon="ShieldCheck"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showRoleModal = false },
        { label: 'Change role', color: 'blue', action: onConfirmChangeRole },
      ]"
      @close="showRoleModal = false">
    <template #header>Change role</template>
    <p class="text-sm text-gray-600">
      Change
      <span class="font-semibold text-gray-800">{{ userToChangeRole?.email }}</span>
      from
      <span class="font-semibold">{{ userToChangeRole?.role }}</span>
      to
      <span class="font-semibold">{{ pendingRole }}</span>?
    </p>
  </Modal>

  <!-- Activate artist modal -->
  <Modal
      v-if="showActivateModal"
      :icon="Zap"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showActivateModal = false },
        { label: 'Activate', color: 'green', action: onConfirmActivate },
      ]"
      @close="showActivateModal = false">
    <template #header>Activate artist</template>
    <p class="text-sm text-gray-600">
      Set <span class="font-semibold text-gray-800">{{ userToActivate?.email }}</span> as the active artist?
      <template v-if="activeArtist && activeArtist.id !== userToActivate?.id">
        <br/>
        <span class="text-yellow-600 font-medium">{{ activeArtist.email }}</span> will be deactivated.
      </template>
    </p>
  </Modal>

</template>

<style scoped>

</style>
