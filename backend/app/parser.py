"""Rule-based event parser with basic Chinese time expression support."""

import re
from datetime import datetime, timedelta, timezone

from .schemas import EventCreate

CATEGORY_COLORS = {
    'research': '#E45757',
    'meeting': '#4B7BE5',
    'life': '#3FAE6A',
}

# Relative time keywords
_PAST_KEYWORDS = ('昨天', '前天', '刚刚', '之前', '刚才', '上午', '下午', '晚上', '昨晚', '今早')
_FUTURE_KEYWORDS = ('提醒', '明天', '后天', '下周', '周末', '下周', '下月', '年后', '待', '计划')

# Day offsets from "today" (approximate, uses current UTC time)
_DAY_OFFSETS = {
    '明天': 1,
    '后天': 2,
    '大后天': 3,
    '昨天': -1,
    '前天': -2,
}

_HOUR_KEYWORDS = {
    '早上': 8,
    '上午': 9,
    '中午': 12,
    '下午': 14,
    '傍晚': 17,
    '晚上': 19,
    '深夜': 23,
    '今早': 8,
    '昨晚': 21,
    '今晚': 20,
}

_WEEKDAYS = {
    '周一': 0, '星期一': 0,
    '周二': 1, '星期二': 1,
    '周三': 2, '星期三': 2,
    '周四': 3, '星期四': 3,
    '周五': 4, '星期五': 4,
    '周六': 5, '星期六': 5, '周末': 5,
    '周日': 6, '周日': 6, '周日': 6, '星期天': 6, '日': 6,
}

_HOUR_PATTERN = re.compile(r'(\d{1,2})[:：]?(\d{1,2})?\s*[点时點時]')
_DURATION_PATTERN = re.compile(r'(\d+)\s*(?:个)?(?:小时|小时钟|分钟|分钟钟)')
_CATEGORY_KEYWORDS = {
    'meeting': ('组会', '会议', '讨论', '面试', '客户', '约谈', '开会', 'meeting'),
    'life': ('吃饭', '运动', '购物', '通勤', '跑步', '健身', '看电影', '散步', '吃饭'),
}


def _find_day_offset(text: str, now: datetime) -> int:
    """Return day offset from now based on text tokens."""
    for token, offset in _DAY_OFFSETS.items():
        if token in text:
            return offset

    # "下周三" style
    for token, wd in _WEEKDAYS.items():
        prefix = '下'
        key = f'{prefix}{token}'
        if key in text:
            current_wd = now.weekday()
            diff = (wd - current_wd) % 7
            if diff == 0:
                diff = 7
            return diff + 7
        if f'本{token}' in text or f'这{token}' in text:
            current_wd = now.weekday()
            diff = (wd - current_wd) % 7
            return diff

    return 0


def _find_hour(text: str) -> int:
    """Extract hour from text. Returns default 9 if not found."""
    match = _HOUR_PATTERN.search(text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        return hour + minute / 60

    for token, hour in _HOUR_KEYWORDS.items():
        if token in text:
            return hour

    return 9


def _find_duration_hours(text: str) -> int:
    """Extract duration in hours from text."""
    match = _DURATION_PATTERN.search(text)
    if match:
        val = int(match.group(1))
        if '分钟' in text:
            return max(val // 60, 1)
        return val
    return 1


def _detect_tense(text: str) -> str:
    for kw in _PAST_KEYWORDS:
        if kw in text:
            return 'past'
    for kw in ('已', '了', '过', '完成', '结束', '处理', '看', '读', '写', '做了'):
        if kw in text and '提醒' not in text:
            pass
    return 'future'


def _detect_category(text: str) -> str:
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return cat
    return 'research'


def infer_event_rule_based(text: str) -> EventCreate:
    now = datetime.now(tz=timezone.utc)
    lowered = text.lower()

    offset = _find_day_offset(text, now)
    hour = _find_hour(text)
    duration = _find_duration_hours(text)

    start_date = now.date() + timedelta(days=offset)
    start_at = datetime(
        year=start_date.year,
        month=start_date.month,
        day=start_date.day,
        hour=int(hour),
        minute=int((hour % 1) * 60),
        tzinfo=timezone.utc,
    )

    # If past keywords, shift to past
    is_past = any(kw in text for kw in ('昨天', '前天', '刚才', '刚刚'))
    if is_past:
        tense = 'past'
    elif any(kw in text for kw in ('提醒', '明天', '后天', '下周', '周末', '下次', '计划')):
        tense = 'future'
    else:
        # Check if text contains completion markers
        tense = _detect_tense(text)

    end_at = start_at + timedelta(hours=duration)

    category = _detect_category(text)

    return EventCreate(
        id=f'evt_{hash(text) & 0xFFFFFFFF:08x}',
        title=text[:30] or 'Untitled event',
        description='Rule-based fallback parsing result.',
        start_at=start_at,
        end_at=end_at,
        tense=tense,
        category=category,
        color=CATEGORY_COLORS[category],
        source_type='text',
        raw_input=text,
        confidence=0.72,
    )
