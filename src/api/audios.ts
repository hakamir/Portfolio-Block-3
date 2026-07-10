export default {
    uploadAudio: `/api/upload/audio`,
    getOrphans: `/api/orphans/audio`,
    deleteOrphans: `/api/orphans/audio`,
    rollbackOrphans: `/api/orphans/audio/rollback`,
    getOrphanAudiosByUser: (id: string) => `/api/orphans/audio/${id}`
}