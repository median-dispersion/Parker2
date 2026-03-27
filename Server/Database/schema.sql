/* ============================================================================================= */
/* Searches */
/* ============================================================================================= */
CREATE TABLE IF NOT EXISTS searches (

    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    start_index bigint NOT NULL,
    next_index bigint NOT NULL,
    end_index bigint NOT NULL,
    start_date timestamp with time zone NOT NULL DEFAULT now(),
    end_date timestamp with time zone

);

/* ============================================================================================= */
/* Clients */
/* ============================================================================================= */
CREATE TABLE IF NOT EXISTS clients (

    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    name character varying(64) NOT NULL,
    registration_date timestamp with time zone NOT NULL DEFAULT now()

);

/* ============================================================================================= */
/* Job states */
/* ============================================================================================= */
CREATE TYPE job_state AS ENUM (

    'claimed',
    'expired',
    'completed',
    'ended'

);

/* ============================================================================================= */
/* Jobs */
/* ============================================================================================= */
CREATE TABLE IF NOT EXISTS jobs (

    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    search_id bigint NOT NULL references searches(id),
    client_id bigint NOT NULL references clients(id),
    state job_state NOT NULL DEFAULT 'claimed',
    start_index bigint NOT NULL,
    current_index bigint NOT NULL,
    end_index bigint NOT NULL,
    start_date timestamp with time zone NOT NULL DEFAULT now(),
    expiration_date timestamp with time zone,
    completion_date timestamp with time zone,
    end_date timestamp with time zone

);

/* ============================================================================================= */
/* Results */
/* ============================================================================================= */
CREATE TABLE IF NOT EXISTS results (

    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    job_id bigint NOT NULL references jobs(id),
    submission_date timestamp with time zone NOT NULL DEFAULT now(),
    a bigint NOT NULL,
    b bigint NOT NULL,
    c bigint NOT NULL,
    d bigint NOT NULL,
    e bigint NOT NULL,
    f bigint NOT NULL,
    g bigint NOT NULL,
    h bigint NOT NULL,
    i bigint NOT NULL

);