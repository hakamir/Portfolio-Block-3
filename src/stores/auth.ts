import {defineStore} from "pinia";
import {ref} from "vue";
import router from "../router";
import {instance} from "@api/axios.ts";
import authApi from "@api/auth.ts";
import type {Status} from "@/types";


export const useAuthStore = defineStore("auth", () => {
    const token = ref<string | null>()
    const isInitialized = ref<boolean>(false)

    const status = ref<Status>('idle')

    const login = async (email: string, pwd: string) => {
        status.value = 'loading'
        try {
            const res = await instance.post(authApi.login, {email, pwd})
            token.value = res.data.token
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
        } catch {
            token.value = null
        } finally {
            isInitialized.value = true
        }
    }

    const changePassword = async (currentPwd: string, newPwd: string) => {
        await instance.put(authApi.changePassword, {currentPwd, newPwd})
    }

    const isTokenExpired = (token: string) => {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            return payload.exp * 1000 < Date.now()
        } catch {
            return true
        }
    }

    const isAuthenticated = () => {
        if (!token.value) return false;
        if (isTokenExpired(token.value)) {
            logout()
            return false;
        }
        return true;
    }

    return {token, isInitialized, status, login, logout, refresh, changePassword, isAuthenticated}
})