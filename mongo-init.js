db = db.getSiblingDB('Portfolio');

db.createUser({
  user: process.env.MONGODB_USER,
  pwd:  process.env.MONGODB_PASSWORD,
  roles: [{ role: 'readWrite', db: 'Portfolio' }]
});

['artists', 'biography', 'galleries', 'messages', 'users'].forEach(name => {
  db.createCollection(name);
});
