-- Adminer 4.7.7 PostgreSQL dump

\connect "users";

DROP TABLE IF EXISTS "users";
CREATE TABLE "public"."users" (
    "username" character(64) NOT NULL,
    "hash" character(1) NOT NULL
) WITH (oids = false);


-- 2020-10-06 01:00:45.672546+00