-- ================================================================================================
-- Set the updated_at field of a row before updating the row
-- ================================================================================================
CREATE FUNCTION set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN

    -- Set the updated_at timestamp to the current date and time
    NEW.updated_at = clock_timestamp();

    -- Return the updated row
    RETURN NEW;

END;
$$;

-- Create a trigger function that sets the updated_at field when updating a row
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ================================================================================================
-- Insert a row into the job history when the job status changed
-- ================================================================================================
CREATE FUNCTION capture_job_history()
RETURNS trigger
LANGUAGE plpgsql
AS $$
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
$$;

-- Create a trigger that captures the initial state of a newly created job
CREATE TRIGGER capture_job_insert
AFTER INSERT ON jobs
FOR EACH ROW
EXECUTE FUNCTION capture_job_history();

-- Create a trigger that captures any updates on the job status
CREATE TRIGGER capture_job_update
AFTER UPDATE OF status ON jobs
FOR EACH ROW
WHEN (NEW.status IS DISTINCT FROM OLD.status)
EXECUTE FUNCTION capture_job_history();

-- ================================================================================================
-- Allow a worker to claim a job
-- ================================================================================================
CREATE FUNCTION claim_job(
    p_worker_uuid uuid,
    p_size ui64,
    p_timeout_seconds bigint
)
RETURNS jobs
LANGUAGE plpgsql
AS $$

-- Function variables
DECLARE
    v_worker_id bigint;
    v_job_id bigint;
    v_timeout_at timestamp(6) with time zone;
    v_job jobs;
    v_start_index ui64;
    v_end_index ui64;

-- Function logic
BEGIN

    -- Raise an exception if the job size is invalid
    IF p_size IS NULL OR p_size < 1 THEN
        RAISE EXCEPTION 'Invalid size';
    END IF;

    -- Raise an exception if the job timeout is invalid
    IF p_timeout_seconds IS NULL OR p_timeout_seconds < 1 THEN
        RAISE EXCEPTION 'Invalid timeout';
    END IF;

    -- Update the workers active_at value and get its ID
    UPDATE workers
    SET active_at = clock_timestamp()
    WHERE uuid = p_worker_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if no connected worker with the given UUID was found
    IF v_worker_id IS NULL THEN
        RAISE EXCEPTION 'Worker not connected';
    END IF;

    -- Try to find 1 failed job and lock it
    SELECT id
    INTO v_job_id
    FROM jobs
    WHERE status IN ('expired', 'canceled', 'terminated')
    ORDER BY id
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    -- Check if no failed job was found
    IF v_job_id IS NULL THEN

        -- Set the job timeout timestamp
        v_timeout_at := clock_timestamp() - make_interval(secs => p_timeout_seconds);

        -- Try to find 1 stale job that is not yet marked as expired and lock it
        SELECT id
        INTO v_job_id
        FROM jobs
        WHERE status = 'claimed'
        AND updated_at < v_timeout_at
        ORDER BY id
        LIMIT 1
        FOR UPDATE SKIP LOCKED;

        -- Check if a stale job was found then mark it as expired
        IF v_job_id IS NOT NULL THEN
            UPDATE jobs
            SET
                status = 'expired',
                expired_at = clock_timestamp()
            WHERE id = v_job_id;
        END IF;

    END IF;

    -- Check if a failed job was found
    IF v_job_id IS NOT NULL THEN

        -- Reset the job and assigned it to the new worker
        UPDATE jobs
        SET
            status = 'claimed',
            attempt = attempt + 1,
            cancellation_reason = NULL,
            worker_id = v_worker_id,
            index = start_index,
            solutions = 0,
            claimed_at = clock_timestamp(),
            expired_at = NULL,
            canceled_at = NULL,
            terminated_at = NULL
        WHERE id = v_job_id
        RETURNING *
        INTO v_job;

        -- Return the reissued job
        RETURN v_job;

    END IF;

    -- If no failed job was found

    -- Set the next_index of the search to the end_index of the new job
    UPDATE search
    SET next_index = next_index + p_size
    WHERE id = 1
    RETURNING OLD.next_index, NEW.next_index
    INTO v_start_index, v_end_index;

    -- Create the new job for the worker
    INSERT INTO jobs (
        worker_id,
        start_index,
        end_index,
        index
    )
    VALUES (
        v_worker_id,
        v_start_index,
        v_end_index,
        v_start_index
    )
    RETURNING *
    INTO v_job;

    -- Return the newly created job
    RETURN v_job;

END;
$$;