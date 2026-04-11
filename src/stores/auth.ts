import {defineStore} from "pinia";
import {ref} from "vue";
import router from "../router";
import {instance} from "@api/axios.ts";
import authApi from "@api/auth.ts";

export const useAuthStore = defineStore("auth", () => {
    const token = ref<string | null>(localStorage.getItem('token'))

    const login = async (email: string, pwd: string) => {
        const res = await instance.post(authApi.login, {email, pwd})
        token.value = res.data.token
        localStorage.setItem('token', res.data.token)
        await router.push('/dashboard')
    }

    const logout = () => {
        token.value = null
        localStorage.removeItem('token')
        router.push('/')
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

    return {token, login, logout, isAuthenticated}
})