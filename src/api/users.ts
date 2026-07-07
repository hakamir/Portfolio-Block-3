export default {
    getUsers: `/api/users`,
    getUser: (id: string) => `/api/users/${id}`,
    changeUserRole: (id: string) => `/api/users/${id}/role`,
    createUser: `/api/users`,
    deleteUser: (id: string) => `/api/users/${id}`,
    activateUser: (id: string) => `/api/users/${id}/activate`,
}