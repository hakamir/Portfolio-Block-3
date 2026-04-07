import { createWebHistory, createRouter } from "vue-router";
import Home from "./views/home/Home.vue";
import Portfolio from "./views/portfolio/Portfolio.vue";
import Contact from "./views/contact/Contact.vue";

const routes = [
    { path: '/', component: Home },
    { path: '/portfolio', component: Portfolio },
    { path: '/contact', component: Contact },
]

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;