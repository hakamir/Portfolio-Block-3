import {useAuthStore} from "../stores";

export default {
    path: '/login',
    name: 'login',
    component: () => import('../views/login/Login.vue'),
    meta: { requiresAuth: false },
    beforeEnter: () => {
        const authStore = useAuthStore()
        if (authStore.isAuthenticated()) {
            return '/dashboard'
        }
    }
}