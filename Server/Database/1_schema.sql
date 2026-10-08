-- ================================================================================================
-- Custom unsigned 64-Bit integer type
-- ================================================================================================
CREATE DOMAIN ui64 AS numeric(20, 0) CHECK (
    VALUE >= 0
    AND
    VALUE <= 18446744073709551615
);

-- Alternative unsigned 64-Bit integer type using bigint
-- Can be used as a drop in replacement for the numeric ui64 type
-- Is significantly faster than using numeric but only allows values up to 2⁶⁴/2-1
-- CREATE DOMAIN ui64 AS bigint CHECK (VALUE >= 0);

-- ================================================================================================
-- Search table
-- ================================================================================================
CREATE TABLE search (

    -- Search ID
    -- Singleton enforcement by only allowing id = 1
    id bigint PRIMARY KEY CHECK (id = 1),

    -- Search index values
    next_index ui64 NOT NULL,
    completed_index ui64 NOT NULL CHECK (completed_index <= next_index),

    -- Timestamp for when the search was updated
    updated_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp()

);

-- Create the singleton search row
INSERT INTO search (id, next_index, completed_index) VALUES (1, 0, 0);

-- ================================================================================================
-- Worker status type
-- ================================================================================================
CREATE TYPE worker_status AS ENUM (

    -- The worker is connected and active
    'connected',

    -- The worker is disconnected and no longer active
    'disconnected',

    -- The worker was terminated by the manager
    'terminated'

);

-- ================================================================================================
-- Workers table
-- ================================================================================================
CREATE TABLE workers (

    -- Worker identification
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT uuidv4(),

    -- Worker name
    -- Different workers can have the same name, use IDs for identification
    -- Allowed character are "a-z" "A-Z" "0-9" and "-"
    name character varying(64) NOT NULL CHECK (name ~ '^[a-zA-Z0-9-]+$'),

    -- The current status of the worker
    status worker_status NOT NULL DEFAULT 'connected',

    -- Timestamp of when the worker connected
    connected_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp(),

    -- Timestamp of the last time the worker was active
    -- The initial value defaults to the current date and time as the first activity
    active_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp(),

    -- Timestamp of when the worker disconnected
    -- Must be set if the status is "disconnected" else must be "NULL"
    disconnected_at timestamp(6) with time zone CHECK (
        (status = 'disconnected' AND disconnected_at IS NOT NULL)
        OR
        (status != 'disconnected' AND disconnected_at IS NULL)
    ),

    -- Timestamp of when the worker was terminated by the manager
    -- Must be set if the status is "terminated" else must be "NULL"
    terminated_at timestamp(6) with time zone CHECK (
        (status = 'terminated' AND terminated_at IS NOT NULL)
        OR
        (status != 'terminated' AND terminated_at IS NULL)
    )

);

-- ================================================================================================
-- Job status type
-- ================================================================================================
CREATE TYPE job_status AS ENUM (

    -- The job was claimed by a worker and is being processed
    'claimed',

    -- The job expired and can be reissued to a new worker
    'expired',

    -- The job was canceled by a worker and can be reissues to a new worker
    'canceled',

    -- The job was finished by a worker but previous jobs (in order) are not yet completed
    'finished',

    -- The job is completed and all previous jobs (in order) are also completed
    'completed',

    -- The job was terminated by the manager
    'terminated'

);

-- ================================================================================================
-- Jobs table
-- ================================================================================================
CREATE TABLE jobs (

    -- Job identification
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT uuidv4(),

    -- The current status of the job
    -- Any new job defaults to being claimed by a worker
    status job_status NOT NULL DEFAULT 'claimed',

    -- Job attempt
    attempt bigint NOT NULL DEFAULT 1 CHECK (attempt >= 1),

    -- Reason for why a job was canceled
    -- Must be set if status is "canceled" else must be "NULL"
    cancellation_reason TEXT CHECK (
        (status = 'canceled' AND cancellation_reason IS NOT NULL)
        OR
        (status != 'canceled' AND cancellation_reason IS NULL)
    ),

    -- The worker that is currently associated with the job
    worker_id bigint NOT NULL REFERENCES workers(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- Job search bounds
    start_index ui64 NOT NULL UNIQUE,
    end_index ui64 NOT NULL UNIQUE CHECK (end_index > start_index),

    -- The search index the worker has reached
    index ui64 NOT NULL CONSTRAINT jobs_index_check CHECK (
        index >= start_index
        AND
        index <= end_index
    ),

    -- Number of solutions found by the worker in this job attempt
    solutions ui64 NOT NULL DEFAULT 0,

    -- Timestamp of when the job was created
    created_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp(),

    -- Timestamp of when the job was claimed by a worker
    -- Defaults to the current date and time
    claimed_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp(),

    -- Timestamp of when the job was updated
    -- Defaults to the current date and time as the first update
    updated_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp(),

    -- Timestamp of when the job expired
    -- Must be set if the status is "expired" else must be "NULL"
    expired_at timestamp(6) with time zone CHECK (
        (status = 'expired' AND expired_at IS NOT NULL)
        OR
        (status != 'expired' AND expired_at IS NULL)
    ),

    -- Timestamp of when the job was canceled by the worker
    -- Must be set if the status is "canceled" else must be "NULL"
    canceled_at timestamp(6) with time zone CHECK (
        (status = 'canceled' AND canceled_at IS NOT NULL)
        OR
        (status != 'canceled' AND canceled_at IS NULL)
    ),

    -- Timestamp of when the job was finished by the worker
    -- Must be set if the status is "finished" or "completed" else must be "NULL"
    finished_at timestamp(6) with time zone CHECK (
        (status IN ('finished', 'completed') AND finished_at IS NOT NULL)
        OR
        (status NOT IN ('finished', 'completed') AND finished_at IS NULL)
    ),

    -- Timestamp of when the job was completed
    -- Must be set if the status is "completed" else must be "NULL"
    completed_at timestamp(6) with time zone CHECK (
        (status = 'completed' AND completed_at IS NOT NULL)
        OR
        (status != 'completed' AND completed_at IS NULL)
    ),

    -- Timestamp of when the job was terminated by the manager
    -- Must be set if the status is "terminated" else must be "NULL"
    terminated_at timestamp(6) with time zone CHECK (
        (status = 'terminated' AND terminated_at IS NOT NULL)
        OR
        (status != 'terminated' AND terminated_at IS NULL)
    )

);

-- Create an index for the worker_id foreign key
CREATE INDEX jobs_worker_id_index
ON jobs (worker_id);

-- Create a unique index for for the worker_id where the job status is claimed
-- This prevents a worker from claiming 2 jobs at the same time
CREATE UNIQUE INDEX jobs_worker_id_claimed_unique_index
ON jobs (worker_id)
WHERE status = 'claimed';

-- Create an index for the jobs id where the job status is failed
CREATE INDEX jobs_id_failed_index
ON jobs (id)
WHERE status IN ('expired', 'canceled', 'terminated');

-- Create an index for the jobs id where the job status is claimed
CREATE INDEX jobs_id_claimed_index
ON jobs (id)
WHERE status = 'claimed';

-- ================================================================================================
-- Job history table
-- ================================================================================================
CREATE TABLE job_history (

    -- History identification
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT uuidv4(),

    -- Job reference
    job_id bigint NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- Jobs status at the time of capture
    status job_status NOT NULL,

    -- Job attempt at the time of capture
    attempt bigint NOT NULL CHECK (attempt >= 1),

    -- Reason for why the job was canceled
    -- Must be set if status is "canceled" else must be "NULL"
    cancellation_reason TEXT CHECK (
        (status = 'canceled' AND cancellation_reason IS NOT NULL)
        OR
        (status != 'canceled' AND cancellation_reason IS NULL)
    ),

    -- The worker that was associated with the job at the time of capture
    worker_id bigint NOT NULL REFERENCES workers(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- Snapshot of various values at the time of capture
    index ui64 NOT NULL,
    solutions ui64 NOT NULL,

    -- Timestamp of the capture
    captured_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp()

);

-- Create an index for the job_id foreign key
CREATE INDEX job_history_job_id_index
ON job_history (job_id);

-- Create an index for the worker_id foreign key
CREATE INDEX job_history_worker_id_index
ON job_history (worker_id);

-- ================================================================================================
-- Solutions table
-- ================================================================================================
CREATE TABLE solutions (

    -- Solution identification
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    uuid uuid NOT NULL UNIQUE DEFAULT uuidv4(),

    -- The worker that found the solution
    worker_id bigint NOT NULL REFERENCES workers(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- A reference to the job the solution was found in
    job_id bigint NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- Solution values
    a ui64 NOT NULL,
    b ui64 NOT NULL,
    c ui64 NOT NULL,
    d ui64 NOT NULL,
    e ui64 NOT NULL,
    f ui64 NOT NULL,
    g ui64 NOT NULL,
    h ui64 NOT NULL,
    i ui64 NOT NULL,

    -- Timestamp of when the solution was submitted
    submitted_at timestamp(6) with time zone NOT NULL DEFAULT clock_timestamp()

);

-- Create an index for the worker_id foreign key
CREATE INDEX solutions_worker_id_index
ON solutions (worker_id);

-- Create an index for the job_id foreign key
CREATE INDEX solutions_job_id_index
ON solutions (job_id);