export default {
  getGalleries: `/api/gallery`,
  getGalleriesDashboard: `/api/gallery/dashboard`,
  getGalleriesByUser: (id: string) => `/api/gallery/${id}`,
  updateGalleries: `/api/gallery`,
  deleteGallery: (id: string) => `/api/gallery/${id}`,
  uploadImage: `/api/upload/gallery`,
  getOrphans: `/api/orphans/gallery`,
  getOrphanGalleriesByUser: (id: string) => `/api/orphans/gallery/${id}`,
  deleteOrphans: `/api/orphans/gallery`,
  rollbackOrphans: `/api/orphans/gallery/rollback`,
}