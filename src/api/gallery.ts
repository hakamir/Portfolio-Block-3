export default {
  getGalleries: `/api/gallery`,
  updateGalleries: `/api/gallery`,
  deleteGallery: (id: string) => `/api/gallery/${id}`,
  uploadImage: `/api/upload/gallery`,
  getOrphans: `/api/orphans/gallery`,
  deleteOrphans: `/api/orphans/gallery`,
}