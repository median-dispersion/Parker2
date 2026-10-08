-- ================================================================================================
-- Helper function for raising an exception if a function parameters is invalid or missing
-- ================================================================================================
CREATE FUNCTION raise_m0001()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION USING
        ERRCODE = 'M0001',
        MESSAGE = 'Invalid or missing input parameters',
        DETAIL = 'One or more input parameters to the function where invalid or are missing',
        HINT = 'Check the input parameters and try again';
END;
$$;

-- ================================================================================================
-- Helper function for raising an exception if a worker is not connected
-- ================================================================================================
CREATE FUNCTION raise_m0002()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION USING
        ERRCODE = 'M0002',
        MESSAGE = 'Worker not connected',
        DETAIL = 'No connected worker was found matching the identifying parameters',
        HINT = 'Check the input parameters and try again';
END;
$$;

-- ================================================================================================
-- Helper function for raising an exception if no matching job was found
-- ================================================================================================
CREATE FUNCTION raise_m0003()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION USING
        ERRCODE = 'M0003',
        MESSAGE = 'No matching job',
        DETAIL = 'No job was found matching the identifying parameters',
        HINT = 'Check the input parameters and try again';
END;
$$;

-- ================================================================================================
-- Helper function for raising an exception if a worker already claimed a job
-- ================================================================================================
CREATE FUNCTION raise_m0004()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION USING
        ERRCODE = 'M0004',
        MESSAGE = 'Worker already claimed a job',
        DETAIL = 'The provided worker already claimed a job',
        HINT = 'The worker must finish or cancel the job before claiming a new one';
END;
$$;

-- ================================================================================================
-- Set the updated_at field of a row before updating
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

-- Create a trigger that automatically set the updated_at field of the search
CREATE TRIGGER search_update_trigger
BEFORE UPDATE ON search
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ================================================================================================
-- Insert a row into the job history table
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
    RETURN NULL;

END;
$$;

-- Create a trigger that captures the initial state of a newly created job
CREATE TRIGGER jobs_insert_trigger
AFTER INSERT ON jobs
FOR EACH ROW
EXECUTE FUNCTION capture_job_history();

-- Create a trigger that captures any updates on the job status
CREATE TRIGGER jobs_update_trigger
AFTER UPDATE OF status ON jobs
FOR EACH ROW
WHEN (NEW.status IS DISTINCT FROM OLD.status)
EXECUTE FUNCTION capture_job_history();

-- ================================================================================================
-- Disconnect a worker
-- ================================================================================================
CREATE FUNCTION disconnect_worker(p_uuid uuid)
RETURNS void
LANGUAGE plpgsql
AS $$

-- Function variables
DECLARE v_worker_id bigint;

-- Function logic
BEGIN

    -- Raise an exception if the input parameters are invalid or missing
    IF p_uuid IS NULL THEN PERFORM raise_m0001(); END IF;

    -- Try to disconnect the worker
    UPDATE workers
    SET
        status = 'disconnected',
        active_at = clock_timestamp(),
        disconnected_at = clock_timestamp()
    WHERE uuid = p_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if the worker is not connected
    IF v_worker_id IS NULL THEN PERFORM raise_m0002(); END IF;

    -- Terminate all claimed jobs from this worker
    UPDATE jobs
    SET
        status = 'terminated',
        terminated_at = clock_timestamp()
    WHERE worker_id = v_worker_id
    AND status = 'claimed';

END;
$$;

-- ================================================================================================
-- Claim a job
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

    -- Raise an exception if the input parameters are invalid or missing
    IF
        p_worker_uuid IS NULL OR
        p_size IS NULL OR p_size < 1 OR
        p_timeout_seconds IS NULL OR p_timeout_seconds < 1
    THEN
        PERFORM raise_m0001();
    END IF;

    -- Try to update the worker and get its ID
    UPDATE workers
    SET active_at = clock_timestamp()
    WHERE uuid = p_worker_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if the worker is not connected
    IF v_worker_id IS NULL THEN PERFORM raise_m0002(); END IF;

    -- Raise an exception if the worker already claimed a job
    IF EXISTS (SELECT FROM jobs WHERE worker_id = v_worker_id AND status = 'claimed') THEN
        PERFORM raise_m0004();
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

        -- Get the timeout timestamp
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
            updated_at = clock_timestamp(),
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

-- ================================================================================================
-- Update a job
-- ================================================================================================
CREATE FUNCTION update_job(
    p_uuid uuid,
    p_attempt bigint,
    p_worker_uuid uuid,
    p_index ui64,
    p_solutions ui64
)
RETURNS void
LANGUAGE plpgsql
AS $$

-- Function variables
DECLARE v_worker_id bigint;

-- Function logic
BEGIN

    -- Raise an exception if the input parameters are invalid or missing
    IF
        p_uuid IS NULL OR
        p_attempt IS NULL OR p_attempt < 1 OR
        p_worker_uuid IS NULL OR
        p_index IS NULL OR
        p_solutions IS NULL
    THEN
        PERFORM raise_m0001();
    END IF;

    -- Try to update the worker and get its ID
    UPDATE workers
    SET active_at = clock_timestamp()
    WHERE uuid = p_worker_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if the worker is not connected
    IF v_worker_id IS NULL THEN PERFORM raise_m0002(); END IF;

    -- Try to update the job
    -- Only allow the job update to advance the values never regress
    UPDATE jobs
    SET
        index = p_index,
        solutions = p_solutions,
        updated_at = clock_timestamp()
    WHERE uuid = p_uuid
    AND status = 'claimed'
    AND attempt = p_attempt
    AND worker_id = v_worker_id
    AND index <= p_index
    AND solutions <= p_solutions;

    -- Raise an exception if the job is not found
    IF NOT FOUND THEN PERFORM raise_m0003(); END IF;

END;
$$;

-- ================================================================================================
-- Cancel a job
-- ================================================================================================
CREATE FUNCTION cancel_job(
    p_uuid uuid,
    p_attempt bigint,
    p_cancellation_reason text,
    p_worker_uuid uuid
)
RETURNS void
LANGUAGE plpgsql
AS $$

-- Function variables
DECLARE v_worker_id bigint;

-- Function logic
BEGIN

    -- Raise an exception if the input parameters are invalid or missing
    IF
        p_uuid IS NULL OR
        p_attempt IS NULL OR p_attempt < 1 OR
        p_cancellation_reason IS NULL OR p_cancellation_reason = '' OR
        p_worker_uuid IS NULL
    THEN
        PERFORM raise_m0001();
    END IF;

    -- Try to update the worker and get its ID
    UPDATE workers
    SET active_at = clock_timestamp()
    WHERE uuid = p_worker_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if the worker is not connected
    IF v_worker_id IS NULL THEN PERFORM raise_m0002(); END IF;

    -- Try to cancel the job
    UPDATE jobs
    SET
        status = 'canceled',
        cancellation_reason = p_cancellation_reason,
        canceled_at = clock_timestamp()
    WHERE uuid = p_uuid
    AND status = 'claimed'
    AND attempt = p_attempt
    AND worker_id = v_worker_id;

    -- Raise an exception if the job is not found
    IF NOT FOUND THEN PERFORM raise_m0003(); END IF;

END;
$$;

-- ================================================================================================
-- Finish a job
-- ================================================================================================
CREATE FUNCTION finish_job(
    p_uuid uuid,
    p_attempt bigint,
    p_worker_uuid uuid,
    p_solutions ui64
)
RETURNS void
LANGUAGE plpgsql
AS $$

-- Function variables
DECLARE
    v_worker_id bigint;
    v_completed_index ui64;
    v_end_index ui64;
    v_completed_jobs_count bigint;

-- Function logic
BEGIN

    -- Raise an exception if the input parameters are invalid or missing
    IF
        p_uuid IS NULL OR
        p_attempt IS NULL OR p_attempt < 1 OR
        p_worker_uuid IS NULL OR
        p_solutions IS NULL
    THEN
        PERFORM raise_m0001();
    END IF;

    -- Try to update the worker and get its ID
    UPDATE workers
    SET active_at = clock_timestamp()
    WHERE uuid = p_worker_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if the worker is not connected
    IF v_worker_id IS NULL THEN PERFORM raise_m0002(); END IF;

    -- Try to finish the job
    UPDATE jobs
    SET
        status = 'finished',
        index = end_index,
        solutions = p_solutions,
        updated_at = clock_timestamp(),
        finished_at = clock_timestamp()
    WHERE uuid = p_uuid
    AND status = 'claimed'
    AND attempt = p_attempt
    AND worker_id = v_worker_id
    AND solutions <= p_solutions;

    -- Raise an exception if the job is not found
    IF NOT FOUND THEN PERFORM raise_m0003(); END IF;

    -- Select the current completed index of the search and lock it
    SELECT completed_index
    INTO v_completed_index
    FROM search
    WHERE id = 1
    FOR UPDATE;

    -- Set the last completed job end index to the current completed index of the search
    v_end_index := v_completed_index;

    -- Set the number of completed jobs to 0
    v_completed_jobs_count := 0;

    -- Loop over the finished jobs
    LOOP

        -- Complete 1 finished job
        -- Where the start index of the finished job
        -- Overlaps with the end index of the last completed job
        -- This completed all finished jobs in order without gaps
        UPDATE jobs
        SET
            status = 'completed',
            completed_at = clock_timestamp()
        WHERE start_index = v_end_index
        AND status = 'finished'
        RETURNING end_index
        INTO v_end_index;

        -- If no job was completed exit the loop
        IF v_end_index IS NULL THEN
            EXIT;
        END IF;

        -- If a job was completed advance the completed index and increase the count
        v_completed_index := v_end_index;
        v_completed_jobs_count := v_completed_jobs_count + 1;

    END LOOP;

    -- Advance the completed index of the search to the end index of the last completed job
    -- If at least 1 job was completed
    IF v_completed_jobs_count > 0 THEN
        UPDATE search
        SET completed_index = v_completed_index
        WHERE id = 1;
    END IF;

END;
$$;

-- ================================================================================================
-- Submit a solution
-- ================================================================================================
CREATE FUNCTION submit_solution(
    p_worker_uuid uuid,
    p_job_uuid uuid,
    p_a ui64,
    p_b ui64,
    p_c ui64,
    p_d ui64,
    p_e ui64,
    p_f ui64,
    p_g ui64,
    p_h ui64,
    p_i ui64
)
RETURNS void
LANGUAGE plpgsql
AS $$

-- Function variables
DECLARE
    v_worker_id bigint;
    v_job_id bigint;

-- Function logic
BEGIN

    -- Raise an exception if the input parameters are invalid or missing
    IF
        p_worker_uuid IS NULL OR
        p_job_uuid IS NULL OR
        p_a IS NULL OR
        p_b IS NULL OR
        p_c IS NULL OR
        p_d IS NULL OR
        p_e IS NULL OR
        p_f IS NULL OR
        p_g IS NULL OR
        p_h IS NULL OR
        p_i IS NULL
    THEN
        PERFORM raise_m0001();
    END IF;

    -- Try to update the worker and get its ID
    UPDATE workers
    SET active_at = clock_timestamp()
    WHERE uuid = p_worker_uuid
    AND status = 'connected'
    RETURNING id
    INTO v_worker_id;

    -- Raise an exception if the worker is not connected
    IF v_worker_id IS NULL THEN PERFORM raise_m0002(); END IF;

    -- Get the job ID and lock it
    -- The lock isn't really necessary
    -- But it prevents the job form being change before the solution is submitted
    SELECT id
    INTO v_job_id
    FROM jobs
    WHERE uuid = p_job_uuid
    AND status = 'claimed'
    FOR UPDATE;

    -- Raise an exception if the job is not found
    IF v_job_id IS NULL THEN PERFORM raise_m0003(); END IF;

    -- Insert the solution
    INSERT INTO solutions(
        worker_id,
        job_id,
        a, b ,c,
        d, e, f,
        g, h, i
    ) VALUES (
        v_worker_id,
        v_job_id,
        p_a, p_b, p_c,
        p_d, p_e, p_f,
        p_g, p_h, p_i
    );

END;
$$;