import {defineStore} from "pinia";
import {computed, ref} from "vue";
import {instance} from "../api/axios.ts";
import messageApi from "../api/messages.ts"
import type {Tab} from "@/types"

export interface Message {
    _id: string;
    name: string;
    email: string;
    message: string;
    date: Date;
    read: boolean;
    trashed: boolean;
    replied: boolean;
}

export const useMessagesStore = defineStore('messages', () => {
    const allMessages = ref<Message[]>([])
    const currentTab = ref<Tab>('inbox')
    const fetchStatus = ref<'idle' | 'loading' | 'error'>('idle')

    // filter messages based on the current tab
    const filteredMessages = computed(() =>
        allMessages.value
            .filter(m => currentTab.value === 'inbox' ? !m.trashed : m.trashed)
            .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    )

    const getMessageById = (id: string) => {
        return allMessages.value.find(m => m._id === id)
    }

    // load messages from API
    const fetchMessages = async () => {
        fetchStatus.value = 'loading'
        try {
            const res = await instance.get(messageApi.getMessages)
            allMessages.value = res.data
            fetchStatus.value = 'idle'
        } catch (error) {
            fetchStatus.value = 'error'
        }
    }

    // mark a message as read
    const markAsRead = async (messageId: string, bool: boolean) => {
        try {
            await instance.patch(messageApi.updateMessage(messageId), {read: bool})
            const message = allMessages.value.find(m => m._id === messageId)
            if (message) message.read = bool
        } catch (error) {
            console.error('Failed to mark message as read:', error)
        }
    }

    // mark a message as trashed
    const markAsTrashed = async (messageId: string, bool: boolean) => {
        try {
            await instance.patch(messageApi.updateMessage(messageId), {trashed: bool})
            const message = allMessages.value.find(m => m._id === messageId)
            if (message) message.trashed = bool
        } catch (error) {
            console.error('Failed to trash message:', error)
        }
    }

    // mark a message as replied
    const markAsReplied = async (messageId: string, bool: boolean) => {
        try {
            await instance.patch(messageApi.updateMessage(messageId), {replied: bool})
            const message = allMessages.value.find(m => m._id === messageId)
            if (message) message.replied = bool
        } catch (error) {
            console.error('Failed to mark message as replied:', error)
        }
    }

    // delete a message
    const deleteMessage = async (messageId: string) => {
        try {
            await instance.delete(messageApi.deleteMessage(messageId))
            allMessages.value = allMessages.value.filter(m => m._id !== messageId)
        } catch (error) {
            console.error('Failed to delete message:', error)
        }
    }

    // apply an action to selected messages
    const applyToSelected = async (ids: string[] | undefined, action: (id: string) => Promise<void>) => {
        if (!ids || ids.length === 0) return
        await Promise.all(ids.map(id => action(id)))
    }

    return {
        allMessages, currentTab, fetchStatus, filteredMessages,
        fetchMessages, markAsRead, markAsTrashed, markAsReplied, deleteMessage, applyToSelected, getMessageById
    }
})