import {useAuthStore} from "@stores";

export default {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@views/dashboard/DashboardLayout.vue'),
    meta: {requiresAuth: true},
    beforeEnter: () => {
        const authStore = useAuthStore()
        if (!authStore.isAuthenticated()) {
            return '/login'
        }
    },
    children: [
        {
            path: '',
            redirect: {name: 'dashboard-messages'}
        },
        {
            path: 'messages',
            name: 'dashboard-messages',
            component: () => import('@views/dashboard/messages/MessagesView.vue'),
        },
        {
            path: 'biography',
            name: 'dashboard-biography',
            component: () => import('@views/dashboard/biography/BiographyView.vue'),
        },
        {
            path: 'works',
            name: 'dashboard-works',
            component: () => import('@views/dashboard/works/WorksView.vue'),
        },
        {
            path: 'settings',
            name: 'dashboard-settings',
            component: () => import('@views/dashboard/settings/SettingsView.vue'),
        }
    ]
}