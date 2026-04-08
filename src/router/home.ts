export default {
    path: '/',
    name: 'home',
    component: () => import('@views/home/Home.vue'),
    meta: { requiresAuth: false },
}