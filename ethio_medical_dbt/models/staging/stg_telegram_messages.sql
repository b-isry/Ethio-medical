select
    -- Extracting fields from the JSONB column
    (message_jsonb ->> 'id')::bigint as message_id,
    (message_jsonb ->> 'date')::timestamp with time zone as message_ts,
    (message_jsonb ->> 'message') as message_text,
    (message_jsonb ->> 'views')::integer as view_count,
    channel_name as channel_handle,
    (message_jsonb -> 'photo' ->> 'id') is not null as has_image

from {{ source('raw_data', 'raw_messages') }}


where (message_jsonb ->> '_') = 'Message'