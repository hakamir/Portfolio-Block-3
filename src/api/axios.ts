import axios from 'axios';
import {useAuthStore} from "@stores";

export const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
});

instance.interceptors.request.use((config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
})

instance.interceptors.response.use(
    res => res,
    async err => {
        const authStore = useAuthStore();
        const url = err.config.url ?? ''

        if (err.response?.status === 401 && !err.config._retry && !url.includes('/auth/login') && !url.includes('/auth/refresh')) {
            err.config._retry = true
            try {
                await authStore.refresh()
                err.config.headers['Authorization'] = `Bearer ${authStore.token}`
                return instance(err.config)
            } catch {
                await authStore.logout()
            }
        }

        return Promise.reject(err)
    }
)