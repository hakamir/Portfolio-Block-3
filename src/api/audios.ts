export default {
    getAudios: `/api/artists`,
    updateAudios: `/api/artists`,
    deleteArtist: (id: string) => `/api/artists/${id}`,
    uploadAudio: `/api/audio/upload`,
    getOrphans: `/api/audio/orphans`,
    deleteOrphans: `/api/audio/orphans`,
}