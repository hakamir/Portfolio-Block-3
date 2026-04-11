import axios from 'axios';
import {useAuthStore} from "@stores";

export const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL
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
    err => {
        // Logout if token is expired and exclude login endpoint to avoid redirection of login failure
        if (err.response.status === 401 && !err.config.url?.includes('/auth/login')) {
            const authStore = useAuthStore();
            authStore.logout();
        }
        return Promise.reject(err);
    }
)