-- ================================================================================================
-- Worker status type
-- ================================================================================================
CREATE TYPE worker_status AS ENUM (
    'connected',
    'disconnected',
    'terminated'
);

-- ================================================================================================
-- Workers table
-- ================================================================================================
CREATE TABLE workers (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT uuidv4(),
    name character varying(64) NOT NULL CHECK (name ~ '^[a-zA-Z0-9-]+$'),
    status worker_status NOT NULL DEFAULT 'connected',
    connected_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    disconnected_at timestamp(6) with time zone,
    terminated_at timestamp(6) with time zone
);