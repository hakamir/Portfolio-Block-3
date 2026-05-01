import axios from 'axios';
import {useAuthStore} from "@stores";
import {getCookie} from "@utils/cookies.ts";

export const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
});

instance.interceptors.request.use((config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`;
    }

    if (['post', 'put', 'patch', 'delete'].includes(config.method ?? '')) {
        const csrfToken = getCookie('csrf_refresh_token')
        if (csrfToken) {
            config.headers['X-CSRF-Token'] = csrfToken
        }
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