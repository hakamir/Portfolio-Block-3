<script setup lang="ts">
import {useRoute, useRouter} from "vue-router"
import {computed, onMounted, ref} from "vue"
import {useUserStore, useAuthStore, useBiographyStore} from "@stores"
import {Undo2, Trash2, ShieldCheck, Zap, PlusCircle, PackageOpen, BookOpen, Music2} from "@lucide/vue"
import Tooltip from "@components/layout/Tooltip.vue"
import Modal from "@components/Modal.vue"
import UserField from "@views/dashboard/admin/components/UserField.vue"
import {instance} from "@api/axios"
import biographyApi from "@api/biography"
import artistsApi from "@api/artists"
import galleryApi from "@api/gallery"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const authStore = useAuthStore()


const biographyStore = useBiographyStore()

const user = computed(() =>
    userStore.users?.find(u => u.id === route.params.id)
)

const isSelf = computed(() => user.value?.id === authStore.payload?.sub)

const pendingRole = computed(() =>
    user.value?.role === 'artist' ? 'admin' : 'artist'
)

const activeArtist = computed(() =>
    userStore.users?.find(u => u.role === 'artist' && u.is_active) ?? null
)

// --- Biography ---
const biography = ref<any>(null)
const biographyLoading = ref(false)

const fetchBiography = async (userId: string) => {
  biographyLoading.value = true
  try {
    const res = await instance.get(biographyApi.getBiographyByUser(userId))
    biography.value = res.data.biography
  } catch (e: any) {
    biography.value = null
  } finally {
    biographyLoading.value = false
  }
}

// --- Artists ---
const artists = ref<any[]>([])
const artistsLoading = ref(false)

const fetchArtists = async (userId: string) => {
  artistsLoading.value = true
  try {
    const res = await instance.get(artistsApi.getArtistsByUser(userId))
    artists.value = res.data
  } catch {
    artists.value = []
  } finally {
    artistsLoading.value = false
  }
}

const galleries = ref<any[]>([])
const galleriesLoading = ref(false)

const fetchGalleries = async (userId: string) => {
  galleriesLoading.value = true
  try {
    const res = await instance.get(galleryApi.getGalleriesByUser(userId))
    galleries.value = res.data
  } catch {
    galleries.value = []
  } finally {
    galleriesLoading.value = false
  }
}

// --- Modals ---
const showDeleteUserModal = ref(false)
const showDeleteBiographyModal = ref(false)
const showRoleModal = ref(false)
const showActivateModal = ref(false)
const showCreateBioModal = ref(false)

const onConfirmDeleteUser = async () => {
  if (!user.value) return
  await userStore.deleteUser(user.value.id)
  showDeleteUserModal.value = false
  router.push('/dashboard')
}

const onConfirmChangeRole = async () => {
  if (!user.value) return
  await userStore.changeUserRole(user.value.id, pendingRole.value)
  showRoleModal.value = false
}

const onConfirmActivate = async () => {
  if (!user.value) return
  await userStore.activateUser(user.value.id)
  showActivateModal.value = false
}

const onConfirmCreateBio = async () => {
  if (!user.value) return
  await biographyStore.createBiography(user.value.id)
  showCreateBioModal.value = false
  await fetchBiography(user.value.id)
}

const onConfirmDeleteBio = async () => {
  if (!user.value) return
  await biographyStore.deleteBiography(user.value.id)
  showDeleteBiographyModal.value = false
  await fetchBiography(user.value.id)
}

onMounted(async () => {
  if (!userStore.users?.length) {
    await userStore.getUsers()
  }
  if (user.value?.role === 'artist') {
    const userId = route.params.id as string
    await Promise.all([fetchBiography(userId), fetchArtists(userId), fetchGalleries(userId)])
  }
})
</script>

<template>
  <div class="border border-gray-200 bg-gray-50 rounded-xl p-6">

    <!-- Header -->
    <div class="mb-6 flex items-start gap-4">
      <Tooltip message="Back to user list">
        <RouterLink to="/dashboard"
                    class="p-1.5 border border-gray-300 bg-white rounded-full hover:scale-105 transition hover:text-blue-600 flex shrink-0">
          <Undo2/>
        </RouterLink>
      </Tooltip>
      <div class="grow min-w-0">
        <h2 class="text-2xl font-unbounded font-semibold">User details</h2>
        <p v-if="user" class="text-sm text-gray-500 mt-0.5 truncate">{{ user.email }}</p>
      </div>
      <div v-if="user" class="flex items-center gap-2 shrink-0">
        <span v-if="user.is_active"
              class="text-xs font-semibold px-2.5 py-1 rounded-full text-white bg-green-700 select-none">Active</span>
        <span
            class="text-xs font-semibold px-2.5 py-1 rounded-full border select-none"
            :class="user.role === 'admin'
              ? 'bg-lime-100 text-lime-800 border-lime-200'
              : 'bg-blue-100 text-blue-800 border-blue-200'">
          {{ user.role }}
        </span>
      </div>
    </div>

    <div v-if="!user" class="text-sm text-gray-500">No user found.</div>

    <div v-else class="flex flex-col gap-6">

      <!-- === Fields === -->
      <div class="grid gap-y-2 grid-cols-[max-content_1fr]">
        <UserField label="Email" :value="user.email" clipboard/>
        <UserField label="ID" :value="user.id" clipboard/>
        <UserField label="Role" :value="user.role"/>
        <UserField label="Status" :value="user.is_active ? 'Active' : 'Inactive'"/>
      </div>

      <!-- === Admin actions === -->
      <div v-if="!isSelf" class="border-t border-gray-200 pt-5">
        <h3 class="text-md font-semibold text-gray-500 uppercase tracking-widest mb-3">Admin actions</h3>
        <div class="flex flex-wrap gap-2">

          <button
              v-if="user.role === 'artist' && !user.is_active"
              @click="showActivateModal = true"
              class="flex items-center gap-2 bg-lime-600 hover:bg-lime-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition">
            <Zap class="w-4 h-4"/>
            Set as active artist
          </button>

          <button
              v-if="!user.is_active"
              @click="showRoleModal = true"
              class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition">
            <ShieldCheck class="w-4 h-4"/>
            Switch to {{ pendingRole }}
          </button>

          <button
              v-if="!user.is_active"
              @click="showDeleteUserModal = true"
              class="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold px-4 py-2 rounded-xl transition">
            <Trash2 class="w-4 h-4"/>
            Delete user
          </button>

          <span v-if="user.is_active" class="text-md text-gray-400 italic">
            Actions are disabled while a user is active.
          </span>
        </div>
      </div>

      <!-- Biography (artists only) -->
      <div v-if="user.role === 'artist'" class="border-t border-gray-200 pt-5">
        <h3 class="text-md font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
          <BookOpen class="w-3.5 h-3.5"/>
          Biography
        </h3>

        <div v-if="biographyLoading" class="text-sm text-gray-400">Loading…</div>

        <div v-else-if="biography"
             class="bg-white border border-gray-200 rounded-xl p-4 flex justify-between">
          <div class="flex flex-col gap-2">
            <p class="text-sm font-semibold text-gray-800 truncate">
              {{ biography.title || '(no title)' }}
            </p>
            <p class="text-xs text-gray-500">
              {{ biography.sections?.length ?? 0 }} section{{ biography.sections?.length === 1 ? '' : 's' }}
            </p>
            <ul v-if="biography.sections?.length"
                class="text-xs text-gray-600 space-y-0.5 pl-2 border-l-2 border-gray-100">
              <li v-for="(section, i) in biography.sections" :key="i" class="truncate">
                {{ section.title || '(unnamed section)' }}
              </li>
            </ul>
          </div>
          <div v-if="!user.is_active" class="flex items-center">
            <button @click="showDeleteBiographyModal=true"
                    class="px-2 py-1 rounded-full text-red-500 text-sm hover:bg-red-100 transition flex items-center gap-1 self-start md:self-auto">
              <Trash2 class="w-4 h-4"/>
              Delete biography
            </button>
          </div>
        </div>

        <button
            v-else
            @click="showCreateBioModal = true"
            class="flex items-center gap-2 border border-dashed border-gray-300 text-gray-500 hover:border-lime-500 hover:text-lime-700 text-sm px-4 py-2.5 rounded-xl transition">
          <PlusCircle class="w-4 h-4"/>
          Create biography
        </button>
      </div>

      <!-- Artist data (artists only) -->
      <div v-if="user.role === 'artist'" class="border-t border-gray-200 pt-5">
        <h3 class="text-md font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
          <Music2 class="w-3.5 h-3.5"/>
          Artists
        </h3>

        <div v-if="artistsLoading" class="text-sm text-gray-400">Loading…</div>

        <div v-else-if="artists.length" class="flex flex-col gap-2">
          <div v-for="artist in artists" :key="artist._id"
               class="bg-white border border-gray-200 rounded-xl p-4">
            <p class="text-sm font-semibold text-gray-800">{{ artist.title }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ artist.albums?.length ?? 0 }}
              album{{ artist.albums?.length === 1 ? '' : 's' }}</p>
            <ul v-if="artist.albums?.length"
                class="mt-2 text-xs text-gray-600 space-y-1 pl-2 border-l-2 border-gray-100">
              <li v-for="album in artist.albums" :key="album._id">
                {{ album.title }}
                <span class="text-gray-400">· {{
                    album.tracks?.length ?? 0
                  }} track{{ album.tracks?.length === 1 ? '' : 's' }}</span>
              </li>
            </ul>
          </div>
        </div>


        <div v-else class="flex items-center gap-2 text-sm text-gray-400">
          <PackageOpen class="w-4 h-4"/>
          No artist data found.
        </div>
      </div>

      <!-- Galleries data -->
      <div v-if="user.role === 'artist'" class="border-t border-gray-200 pt-5">
        <h3 class="text-md font-semibold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
          <Music2 class="w-3.5 h-3.5"/>
          Galleries
        </h3>

        <div v-if="galleriesLoading" class="text-sm text-gray-400">Loading…</div>

        <div v-else-if="galleries.length" class="flex flex-col gap-2">
          <div v-for="gallery in galleries" :key="gallery._id"
               class="bg-white border border-gray-200 rounded-xl p-4">
            <p class="text-sm font-semibold text-gray-800">{{ gallery.title }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ gallery.images?.length ?? 0 }}
              image{{ gallery.images?.length === 1 ? '' : 's' }}</p>
            <ul v-if="gallery.images?.length"
                class="mt-2 text-xs text-gray-600 space-y-1 pl-2 border-l-2 border-gray-100">
              <li v-for="image in gallery.images" :key="image._id">
                {{ image.alt }}
              </li>
            </ul>
          </div>
        </div>


        <div v-else class="flex items-center gap-2 text-sm text-gray-400">
          <PackageOpen class="w-4 h-4"/>
          No gallery data found.
        </div>
      </div>

    </div>
  </div>

  <!-- Delete user modal -->
  <Modal
      v-if="showDeleteUserModal"
      :icon="Trash2"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showDeleteUserModal = false },
        { label: 'Delete', color: 'red', action: onConfirmDeleteUser },
      ]"
      @close="showDeleteUserModal = false">
    <template #header>Delete user</template>
    <p class="text-sm text-gray-600">
      Are you sure you want to delete
      <span class="font-semibold text-gray-800">{{ user?.email }}</span>?
      This action cannot be undone.
    </p>
  </Modal>

  <!-- Delete biography modal -->
  <Modal
      v-if="showDeleteBiographyModal"
      :icon="Trash2"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showDeleteBiographyModal = false },
        { label: 'Delete', color: 'red', action: onConfirmDeleteBio },
      ]"
      @close="showDeleteBiographyModal = false">
    <template #header>Delete biography</template>
    <p class="text-sm text-gray-600">
      Are you sure you want to delete the biography of
      <span class="font-semibold text-gray-800">{{ user?.email }}</span>?<br/>
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
      Change <span class="font-semibold text-gray-800">{{ user?.email }}</span> from
      <span class="font-semibold">{{ user?.role }}</span> to
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
      Set <span class="font-semibold text-gray-800">{{ user?.email }}</span> as the active artist?
      <template v-if="activeArtist && activeArtist.id !== user?.id">
        <br/>
        <span class="text-yellow-600 font-medium">{{ activeArtist.email }}</span> will be deactivated.
      </template>
    </p>
  </Modal>

  <!-- Create biography modal -->
  <Modal
      v-if="showCreateBioModal"
      :icon="BookOpen"
      :buttons="[
        { label: 'Cancel', color: 'white', action: () => showCreateBioModal = false },
        { label: 'Create', color: 'green', action: onConfirmCreateBio },
      ]"
      @close="showCreateBioModal = false">
    <template #header>Create biography</template>
    <p class="text-sm text-gray-600">
      Create an empty biography for
      <span class="font-semibold text-gray-800">{{ user?.email }}</span>?
      They will be able to fill it in from their dashboard.
    </p>
  </Modal>
</template>
