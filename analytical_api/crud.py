from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
import re
from . import models


ENGLISH_STOP_WORDS = set([
    'and', 'the', 'for', 'with', 'new', 'available', 'in', 'on', 'at', 'is', 'are', 'a', 'an',
    'of', 'to', 'from', 'price', 'contact', 'info', 'call', 'we', 'have', 'our', 'you', 'your'
])

AMHARIC_STOP_WORDS = set([
    'እና', 'ነው', 'ላይ', 'ጋር', 'ውስጥ', 'ከ', 'ወደ', 'ስለ', 'እንደ', 'በ', 'ግን', 'ወይም',
    'እኔ', 'አንተ', 'አንቺ', 'እሱ', 'እሷ', 'እኛ', 'እናንተ', 'እነሱ', 'ይህ', 'ያ', 'ነገር', 'ሁሉ',
    'ማለት', 'ሆኖ', 'ሲሆን', 'ብቻ', 'ደግሞ', 'እንዳለ', 'ሆነ', 'ናቸው', 'አዲስ', 'ዋጋ', 'መረጃ',
    'ለበለጠ', 'ይደውሉ', 'ያግኙን', 'አለ', 'አለን'
])

ALL_STOP_WORDS = ENGLISH_STOP_WORDS.union(AMHARIC_STOP_WORDS)


def get_top_products(db: Session, limit: int = 10):
    """
    Finds the most frequently mentioned product names.
    This revised version handles both English and Amharic text.
    """
    all_messages = db.query(models.Message.message_text).filter(models.Message.message_text.isnot(None)).all()
    
    word_counts = Counter()
    
    # This regex is designed to replace both English and Amharic punctuation with a space
    # It includes standard punctuation and Amharic specific ones like '።', '፣', '፤', '፡'
    punctuation_remover = re.compile(r"[\.,'\"\-!?:;።፣፤፡]+")

    for (text,) in all_messages:
        # 1. Normalize text to lowercase
        normalized_text = text.lower()
        
        # 2. Replace punctuation with spaces to ensure clean splits
        cleaned_text = punctuation_remover.sub(' ', normalized_text)
        
        # 3. Split text into words (tokens)
        words = cleaned_text.split()
        
        # 4. Filter out stop words and short words
        product_words = [word for word in words if word not in ALL_STOP_WORDS and len(word) > 2]
        
        # 5. Update the counts
        word_counts.update(product_words)
        
    top_products = [{"product": word, "mentions": count} for word, count in word_counts.most_common(limit)]
    return top_products

def search_messages(db: Session, query: str):
    """Searches for messages containing a specific keyword (case-insensitive)."""
    return db.query(models.Message).filter(models.Message.message_text.ilike(f"%{query}%")).all()

def get_channel_activity(db: Session, channel_name: str):
    """Returns the daily posting activity for a specific channel."""
    return db.query(
            func.date_trunc('day', models.Message.message_ts).label('post_date'),
            func.count(models.Message.message_id).label('message_count')
        ).filter(models.Message.clean_channel_name == channel_name)\
        .group_by('post_date')\
        .order_by(func.date_trunc('day', models.Message.message_ts).desc())\
        .all()