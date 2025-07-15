select
    mapping.clean_channel_name,
    msgs.channel_handle
from {{ ref('stg_telegram_messages') }} as msgs
left join {{ ref('channel_mapping') }} as mapping
    on msgs.channel_handle = mapping.channel_handle
group by 1, 2