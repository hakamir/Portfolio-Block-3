import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { instance } from '@api/axios'
import messageApi from '@api/messages'
import type {Status} from '@/types';

interface ContactForm {
    name: string
    email: string
    message: string
    date: string
    read: boolean
    trashed: boolean
}

export const useContactStore = defineStore('contact', () => {
    const formData = reactive<ContactForm>({
        name: '',
        email: '',
        message: '',
        date: new Date().toISOString(),
        read: false,
        trashed: false
    })

    const status = ref<Status>('idle')

    // reset the form to the initial state
    const resetForm = () => {
        formData.name = ''
        formData.email = ''
        formData.message = ''
        formData.date = new Date().toISOString()
        status.value = 'idle'
    }

    // send a message
    const sendMessage = async () => {
        status.value = 'loading'
        try {
            await instance.post(messageApi.createMessage, formData)
            status.value = 'success'
        } catch (error: any) {
            const code = error.response?.status
            if (code === 429) {
                status.value = 'tooMany'
            } else {
                status.value = 'error'
            }
        }
    }

    return { formData, status, resetForm, sendMessage }
})