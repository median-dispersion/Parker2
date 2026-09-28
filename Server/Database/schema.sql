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
    connected_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    -- Timestamp of the last time the worker was active
    -- The initial value defaults to the current date and time as the first activity
    active_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

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
-- Custom unsigned 64-Bit integer type
-- ================================================================================================
CREATE DOMAIN ui64 AS numeric(20, 0) CHECK (
    VALUE >= 0 AND
    VALUE <= 18446744073709551615
);

-- Alternative unsigned 64-Bit integer type using bigint
-- Can be used as a drop in replacement for the numeric ui64 type
-- Is significantly faster than using numeric but only allows values up to 2⁶⁴/2-1
CREATE DOMAIN ui64_2 AS bigint CHECK (VALUE >= 0);

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
    start_index ui64 NOT NULL,
    end_index ui64 NOT NULL CHECK (end_index > start_index),

    -- The search index the worker has reached
    index ui64 NOT NULL CHECK (
        index >= start_index
        OR
        index <= end_index
    ),

    -- Number of solutions found by the worker in this job attempt
    solutions ui64 NOT NULL DEFAULT 0,

    -- Timestamp of when the job was created
    created_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    -- Timestamp of when the job was updated
    -- Defaults to the current date and time as the first update
    -- Is automatically updated by a trigger function
    updated_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    -- Timestamp of when the job was claimed by a worker
    -- Defaults to the current date and time
    claimed_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    -- Timestamp of when the job expired
    -- Must be set if the status is "expired" else must be "NULL"
    expired_at timestamp(6) with time zone CHECK (
        (status = 'expired' AND expired_at IS NOT NULL)
        OR
        (status != 'expired' AND expired_at IS NULL)
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

-- Create indices for the jobs table
CREATE INDEX ON jobs(worker_id);

-- ================================================================================================
-- Trigger function for automatically setting the updated_at field
-- ================================================================================================
CREATE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN

    -- Set the update_at timestamp to the current date and time
    NEW.updated_at = CURRENT_TIMESTAMP(6);

    -- Return the updated row
    RETURN NEW;

END;
$$ LANGUAGE plpgsql;

-- Create a trigger on the jobs table calling the function
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

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
    captured_at timestamp(6) with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(6)

);

-- Create indices for the job_history table
CREATE INDEX ON job_history(job_id);
CREATE INDEX ON job_history(worker_id);

-- ================================================================================================
-- Trigger function that automatically captures the job history
-- ================================================================================================
CREATE FUNCTION capture_job_history() RETURNS trigger AS $$
BEGIN

    -- Insert a snapshot of the job into the job history
    INSERT INTO job_history (
        job_id,
        status,
        attempt,
        cancellation_reason,
        worker_id,
        index,
        solutions
    )
    VALUES (
        NEW.id,
        NEW.status,
        NEW.attempt,
        NEW.cancellation_reason,
        NEW.worker_id,
        NEW.index,
        NEW.solutions
    );

    -- Return (required by PL/pgSQL)
    RETURN NEW;

END;
$$ LANGUAGE plpgsql;

-- Create a trigger that captures the initial state of a newly created job
CREATE TRIGGER capture_job_insert
AFTER INSERT ON jobs
FOR EACH ROW
EXECUTE FUNCTION capture_job_history();

-- Create a trigger that captures any updates on the job state
CREATE TRIGGER capture_job_update
AFTER UPDATE OF status ON jobs
FOR EACH ROW
WHEN (NEW.status IS DISTINCT FROM OLD.status)
EXECUTE FUNCTION capture_job_history();