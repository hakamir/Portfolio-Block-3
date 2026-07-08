export default {
    getBiography: `/api/biography`,
    getBiographyDashboard: `/api/biography/dashboard`,
    getBiographyByUser: (id: string) => `/api/biography/${id}`,
    updateBiography: `/api/biography`,
    createBiography: `/api/biography`,
}