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