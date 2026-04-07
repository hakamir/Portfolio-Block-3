export default {
    path: '/contact',
    name: 'contact',
    component: () => import('../views/contact/Contact.vue'),
    meta: { requiresAuth: false },
}