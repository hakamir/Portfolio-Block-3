export default {
    getArtists: `/api/artists`,
    getArtistsDashboard: `/api/artists/dashboard`,
    getArtistsByUser: (id: string) => `/api/artists/${id}`,
    updateArtists: `/api/artists`,
    deleteArtist: (id: string) => `/api/artists/${id}`,
}