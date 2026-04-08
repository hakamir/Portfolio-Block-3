export default {
    path: '/portfolio',
    name: 'portfolio',
    component: () => import('@views/portfolio/Portfolio.vue'),
    meta: { requiresAuth: false },
}