<script setup lang="ts">
import Footer from "@components/layout/footer/Footer.vue";
import {LoaderCircle, TriangleAlert} from "@lucide/vue";
import {reactive, ref} from "vue";
import {useAuthStore} from "@stores";


interface LoginForm {
  email: string;
  pwd: string;
}

const formData = reactive<LoginForm>({
  email: '',
  pwd: ''
})

const status = ref<'idle' | 'loading' | 'success' | 'error' | 'invalid' | 'tooMany'>('idle')

const authStore = useAuthStore()

const handleSubmit = async () => {
  status.value = 'loading'
  try {
    await authStore.login(formData.email, formData.pwd)
    status.value = 'success'
  } catch (error: any) {
    const code = error.response?.status
    if (code === 401) status.value = 'invalid'
    else if (code === 429) status.value = 'tooMany'
    else status.value = 'error'
  }
}

</script>

<template>
  <div class="flex flex-col min-h-screen">
    <div class="flex flex-1 justify-center">
      <section class="pt-28 pb-16 md:pt-48 container xl:w-4/5 2xl:w-2/3 mx-auto px-8 md:px-32">
        <h1 class="text-4xl font-bold font-unbounded text-center mb-4">Login</h1>
        <div class="flex justify-center">
          <span class="text-gray-500 font-light text-md">Please enter your email and password to login.</span>
        </div>
        <form id="form-contact" class="flex flex-col gap-4" @submit.prevent="handleSubmit">
          <div>
            <label for="email" class="block text-lg font-bold mb-2">Email</label>
            <input id="email" type="email" placeholder="Email" v-model="formData.email"
                   class="border border-gray-300 rounded px-4 py-2 w-full" required>
          </div>
          <div>
            <label for="pwd" class="block text-lg font-bold mb-2">Password</label>
            <input id="pwd" type="password" placeholder="Password" v-model="formData.pwd"
                   class="border border-gray-300 rounded px-4 py-2 w-full" required>
          </div>
          <div class="flex flex-col">
            <div class="flex justify-center">
              <button id="submit-button" type="submit"
                      class="bg-black text-white px-16 py-3 font-unbounded rounded transition-all duration-300 hover:bg-neutral-700 flex items-center justify-center">
                <span v-if="status !== 'loading'">Login</span>
                <LoaderCircle v-else class="animate-spin"/>
              </button>
            </div>
            <div v-if="status === 'invalid'" class="flex justify-center mt-2">
                <span class="px-3 py-2 rounded-xl text-amber-500 bg-amber-100 text-sm flex items-center">
                  <TriangleAlert class="inline-block mr-2"/>
                  Invalid email of password.
                </span>
            </div>
            <div v-else-if="status === 'error'" class="flex justify-center mt-2">
                <span class="px-3 py-2 rounded-xl text-red-500 bg-red-100 text-sm flex items-center">
                  <TriangleAlert class="inline-block mr-2"/>
                  An error occurred while attempting to login. Please try again later.
                </span>
            </div>
            <div v-else-if="status === 'tooMany'" class="flex justify-center mt-2">
              <span class="px-3 py-2 rounded-xl text-amber-500 bg-amber-100 text-sm flex items-center">
                <TriangleAlert class="inline-block mr-2"/>
                Too many login attempts. Please try again later.
              </span>
            </div>
          </div>
        </form>
      </section>
    </div>
    <Footer />
  </div>
</template>
