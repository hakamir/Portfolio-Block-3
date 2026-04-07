import {defineStore} from "pinia";
import {ref} from "vue";
import router from "../router";

export const useAuthStore = defineStore("auth", () => {
    const token = ref<string | null>(localStorage.getItem('token'))

    const login = async (email: string, pwd: string) => {
        const res = await fetch('http://localhost:5000/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({email, pwd}),
        })

        if (res.status === 401) {
            throw new Error('Invalid credentials')
        }
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`)
        }
        const data = await res.json()
        token.value = data.token
        localStorage.setItem('token', data.token)
        router.push('/dashboard')
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

    return { token, login, logout, isAuthenticated }
})