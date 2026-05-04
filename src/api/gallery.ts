export default {
  getGalleries: `/api/gallery`,
  updateGalleries: `/api/gallery`,
  deleteGallery: (id: string) => `/api/gallery/${id}`,
  uploadImage: `/api/gallery/upload`,
}