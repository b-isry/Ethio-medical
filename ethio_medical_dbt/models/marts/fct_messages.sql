select
    message_id,
    message_ts,
    date_trunc('day', message_ts) as date_day,
    coalesce(mapping.clean_channel_name, mapping.channel_handle) as clean_channel_name,
    message_text,
    view_count,
    has_image,
    length(message_text) as message_length
from {{ ref('stg_telegram_messages') }} as msgs
left join {{ ref('channel_mapping') }} as mapping
    on msgs.channel_handle = mapping.channel_handle
where message_text is not null