import { createWebHistory, createRouter } from "vue-router";
import Home from "./components/home/Home.vue";
import Portfolio from "./components/portfolio/Portfolio.vue";
import Contact from "./components/contact/Contact.vue";

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