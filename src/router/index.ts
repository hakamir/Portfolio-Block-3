import { createWebHistory, createRouter } from "vue-router";
import login from "./login.ts";
import home from "./home.ts";
import portfolio from "./portfolio.ts";
import contact from "./contact.ts";
import dashboard from "./dashboard.ts";

const routes = [
    home,
    portfolio,
    contact,
    login,
    dashboard,
    { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;