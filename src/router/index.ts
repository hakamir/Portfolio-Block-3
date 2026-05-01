import { createWebHistory, createRouter } from "vue-router";
import login from "./login.ts";
import home from "./home.ts";
import portfolio from "./portfolio.ts";
import contact from "./contact.ts";
import dashboard from "./dashboard.ts";
import {useAuthStore} from "@stores";

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
router.beforeEach(async (to) => {
    const authStore = useAuthStore()

    if (!authStore.isInitialized) {
        await authStore.refresh()
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated()) {
        return { name: 'login' }
    }
})

export default router;