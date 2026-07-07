export default {
    getArtists: `/api/artists`,
    getArtistsDashboard: `/api/artists/dashboard`,
    updateArtists: `/api/artists`,
    deleteArtist: (id: string) => `/api/artists/${id}`,
}