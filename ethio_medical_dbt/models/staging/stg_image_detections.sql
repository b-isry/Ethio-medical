select
    message_id,
    detected_object,
    confidence_score,
    loaded_at
from {{ source('raw_data', 'raw_image_detections') }}