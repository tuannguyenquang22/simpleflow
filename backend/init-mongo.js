// Simpleflow
db = db.getSiblingDB("simpleflow");

// Init collections
db.createCollection("datasource");
db.createCollection("featureset");
db.createCollection("learner");

// Celery
db = db.getSiblingDB("celery");
db.createCollection("celery_taskmeta");