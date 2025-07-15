select
    message_id,
    detected_object,
    confidence_score
from {{ ref('stg_image_detections') }}