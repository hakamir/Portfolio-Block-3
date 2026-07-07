export default {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@views/dashboard/DashboardLayout.vue'),
    meta: {requiresAuth: true},
    children: [
        {
            path: '',
            name: 'dashboard-home',
            redirect: {name: 'dashboard-messages'}
        },
        {
            path: 'messages',
            name: 'dashboard-messages',
            component: () => import('@views/dashboard/messages/MessagesView.vue'),
            meta: {roles: ['artist']},
            redirect: {name: 'dashboard-messages-list'},
            children: [
                {
                    path: '',
                    name: 'dashboard-messages-list',
                    component: () => import('@views/dashboard/messages/components/MessageLayout.vue'),
                },
                {
                    path: ':id',
                    name: 'dashboard-message-detail',
                    component: () => import('@views/dashboard/messages/components/MessageDetailView.vue'),
                },
            ]
        },

        {
            path: 'biography',
            name: 'dashboard-biography',
            component: () => import('@views/dashboard/biography/BiographyView.vue'),
            meta: {roles: ['artist']},
        },
        {
            path: 'works',
            name: 'dashboard-works',
            component: () => import('@views/dashboard/works/WorksView.vue'),
            meta: {roles: ['artist']},
        },
        {
            path: 'admin',
            name: 'dashboard-admin',
            component: () => import('@views/dashboard/admin/AdminView.vue'),
            meta: {roles: ['admin']},
        },
        {
            path: 'settings',
            name: 'dashboard-settings',
            component: () => import('@views/dashboard/settings/SettingsView.vue'),
            meta: {roles: ['artist', 'admin']},
        }
    ]
}