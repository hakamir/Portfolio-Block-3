<script setup lang="ts">
  import { reactive } from 'vue';

  interface ContactForm {
    name: string;
    email: string;
    message: string;
    date: Date;
    read: boolean;
    trashed: boolean;
  }

  const formData = reactive<ContactForm>({
    name: '',
    email: '',
    message: '',
    date: new Date(),
    read: false,
    trashed: false
  })

  const handleSubmit = async () => {
    await fetch('http://localhost:3001/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
  }
</script>

<template>
  <main class="grow">
    <section class="pt-28 pb-16 md:pt-48 container mx-auto px-8 md:px-32">
      <h1 class="text-4xl font-bold font-unbounded">Contact</h1>
      <div class="md:grid md:grid-cols-2 pt-8 gap-16">
        <div class="pb-8">
          <h2 class="text-2xl font-unbounded">Get in touch!</h2>
          <p class="pt-4">Feel free to reach out to me for any inquiries, collaborations, or just to say hello.
            I'm always open to new opportunities and excited to hear from you!</p>
        </div>
        <form id="form-contact" class="flex flex-col gap-4" @submit.prevent="handleSubmit">
          <div>
            <label for="name" class="block text-lg font-bold mb-2">Name</label>
            <input id="name" type="text" placeholder="Name" v-model="formData.name"
                   class="border border-gray-300 rounded px-4 py-2 w-full" required>
          </div>
          <div>
            <label for="email" class="block text-lg font-bold mb-2">Email</label>
            <input id="email" type="email" placeholder="Email" v-model="formData.email"
                   class="border border-gray-300 rounded px-4 py-2 w-full" required>
          </div>
          <div>
            <label for="message" class="block text-lg font-bold mb-2">Message</label>
            <textarea id="message" placeholder="Message" v-model="formData.message"
                      class="border border-gray-300 rounded px-4 py-2 w-full" required></textarea>
          </div>
          <div class="flex justify-end">
            <button id="submit-button" type="submit"
                    class="bg-black text-white px-6 py-3 font-unbounded rounded transition-all duration-300 hover:bg-neutral-700">
              Send Message
            </button>
          </div>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>

</style>