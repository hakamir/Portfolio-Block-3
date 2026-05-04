export default {
    getMessages: `/api/messages`,
    createMessage: `/api/messages`,
    updateMessage: (id: string) => `/api/messages/${id}`,
    deleteMessage: (id: string) => `/api/messages/${id}`,
}