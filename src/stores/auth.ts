import {defineStore} from "pinia";
import {ref} from "vue";
import router from "@router";
import {jwtDecode} from 'jwt-decode';
import {instance} from "@api/axios.ts";
import authApi from "@api/auth.ts";
import type {Status} from "@/types";


interface JwtPayload {
    sub: string
    role: string
    exp: number
}

export const useAuthStore = defineStore("auth", () => {
    const token = ref<string | null>()
    const isInitialized = ref<boolean>(false)
    const payload = ref<JwtPayload | null>()

    const status = ref<Status>('idle')

    const login = async (email: string, pwd: string) => {
        status.value = 'loading'
        try {
            const res = await instance.post(authApi.login, {email, pwd})
            token.value = res.data.token
            payload.value = jwtDecode<JwtPayload>(token.value!)
            status.value = 'success'
            await router.push('/dashboard')
        } catch (error: any) {
            const code = error.response?.status
            if (code === 401) status.value = 'invalid'
            else if (code === 429) status.value = 'tooMany'
            else status.value = 'error'
        }
    }

    const logout = async () => {
        await instance.post(authApi.logout)
        token.value = null
        await router.push('/')
    }

    const refresh = async () => {
        try {
            const res = await instance.post(authApi.refresh)
            token.value = res.data.token
            payload.value = jwtDecode<JwtPayload>(token.value!)
        } catch {
            token.value = null
        } finally {
            isInitialized.value = true
        }
    }

    const changePassword = async (currentPwd: string, newPwd: string) => {
        status.value = 'loading'
        try {
            await instance.put(authApi.changePassword, {currentPwd, newPwd})
            status.value = 'success'
            // Reset status to idle after a delay to clear success feedback
            setTimeout(() => status.value = 'idle', 3000)
        } catch (error: any) {
            // Map 401 response to 'invalid' (wrong current password), otherwise generic error
            status.value = error.response?.status === 401 ? 'invalid' : 'error'
        }
    }

    // Check if a token exists and is in format "header.payload.signature"
    const isAuthenticated = () => !!token.value && token.value.split('.').length === 3

    return {token, isInitialized, status, payload, login, logout, refresh, changePassword, isAuthenticated}
})