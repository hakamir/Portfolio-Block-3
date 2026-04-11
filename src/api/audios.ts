export default {
    getAudios: `/artists`,
    updateAudios: `/artists`,
    deleteArtist: (id: string) => `/artists/${id}`,
    uploadAudio: `/audio/upload`,
    getOrphans: `/audio/orphans`,
    deleteOrphans: `/audio/orphans`,
}