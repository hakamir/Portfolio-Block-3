import {defineStore} from "pinia";
import {computed, reactive, ref} from "vue";
import { useAuthStore } from "./auth";

interface Message {
    _id?: string;
    name: string;
    email: string;
    message: string;
    date: Date;
    read: boolean;
    trashed: boolean;
}

export type Tab = 'inbox' | 'trash'
type Status = 'idle' | 'loading' | 'submitted' | 'error'

export const useMessagesStore = defineStore('messages', () => {
    const authStore = useAuthStore()
    const allMessages = ref<Message[]>([])
    const currentTab = ref<Tab>('inbox')
    const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')

    const filteredMessages = computed(() =>
        allMessages.value
            .filter(m => currentTab.value === 'inbox' ? !m.trashed : m.trashed)
            .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    )

    function truncateMessage(text: string, maxLength = 50) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    const loadMessages = async () => {
        fetchStatus.value = 'loading'
        try {
            const res = await fetch('http://localhost:5000/messages', {
                headers: {
                    'Authorization': `Bearer ${authStore.token}`,
                },
            })
            if (!res.ok) throw new Error('Failed to fetch messages')
            allMessages.value = await res.json()
            fetchStatus.value = 'idle'
        } catch (error) {
            fetchStatus.value = 'error'
        }
    }

    const markAsRead = async (messageId: string, bool: boolean) => {
        try {
            await fetch(`http://localhost:5000/messages/${messageId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`,
                },
                body: JSON.stringify({read: bool}),
            })
            const message = allMessages.value.find(m => m._id === messageId)
            if (message) message.read = bool
        } catch (error) {
            console.error('Failed to mark message as read:', error)
        }
    }

    const trashMessage = async (messageId: string, bool: boolean) => {
        try {
            await fetch(`http://localhost:5000/messages/${messageId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`,
                },
                body: JSON.stringify({trashed: bool}),
            })
            const message = allMessages.value.find(m => m._id === messageId)
            if (message) message.trashed = bool
        } catch (error) {
            console.error('Failed to trash message:', error)
        }
    }

    const deleteMessage = async (messageId: string) => {
        try {
            await fetch(`http://localhost:5000/messages/${messageId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`,
                },
            })
            allMessages.value = allMessages.value.filter(m => m._id !== messageId)
        } catch (error) {
            console.error('Failed to delete message:', error)
        }
    }

    const applyToSelected = async (ids: string[], action: (id: string) => Promise<void>) => {
        await Promise.all(ids.map(id => action(id)))
    }

    const formData = reactive<Message>({
        name: '',
        email: '',
        message: '',
        date: new Date(),
        read: false,
        trashed: false
    })

    const status = ref<Status>('idle')

    const resetForm = () => {
        formData.name = ''
        formData.email = ''
        formData.message = ''
        formData.date = new Date()
        status.value = 'idle'
    }

    const sendMessage = async () => {
        status.value = 'loading'
        try {
            const res = await fetch('http://localhost:5000/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
            if (!res.ok) throw new Error('Failed to send message')
            status.value = 'submitted'
        } catch (error) {
            status.value = 'error'
        }
    }

    return {
        formData, status, sendMessage, resetForm, allMessages, currentTab, fetchStatus, filteredMessages,
        truncateMessage, loadMessages, markAsRead, trashMessage, deleteMessage, applyToSelected
    }
})