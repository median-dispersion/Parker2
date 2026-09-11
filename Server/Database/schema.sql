CREATE TYPE worker_state AS ENUM (
    'registered',
    'deregistered',
    'terminated'
);

CREATE TABLE workers (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    uuid uuid NOT NULL UNIQUE DEFAULT uuidv4(),
    name character varying(64) NOT NULL,
    state worker_state NOT NULL DEFAULT 'registered',
    registration_date timestamp with time zone NOT NULL DEFAULT now(),
    deregistration_date timestamp with time zone,
    termination_date timestamp with time zone
);