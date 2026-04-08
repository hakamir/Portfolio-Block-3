export default {
    getMessages: `/messages`,
    createMessage: `/messages`,
    updateMessage: (id: string) => `/messages/${id}`,
    deleteMessage: (id: string) => `/messages/${id}`,
}