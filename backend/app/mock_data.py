from datetime import datetime, timedelta, timezone

from .schemas import Event


UTC = timezone.utc
NOW = datetime.now(tz=UTC)

MOCK_EVENTS = [
    Event(
        id="evt_1",
        title="数据库查询优化实验",
        description="整理索引方案并记录实验结果",
        start_at=NOW - timedelta(hours=5),
        end_at=NOW - timedelta(hours=3),
        tense="past",
        category="research",
        color="#E45757",
        raw_input="今天下午两点到四点在处理数据库查询优化和实验",
        confidence=0.93,
    ),
    Event(
        id="evt_2",
        title="组会",
        description="同步本周模型接入进展",
        start_at=NOW + timedelta(days=1, hours=1),
        end_at=NOW + timedelta(days=1, hours=2),
        tense="future",
        category="meeting",
        color="#4B7BE5",
        raw_input="明天下午开组会",
        confidence=0.91,
    ),
    Event(
        id="evt_3",
        title="晚间运动",
        description="慢跑 30 分钟",
        start_at=NOW + timedelta(days=1, hours=6),
        end_at=NOW + timedelta(days=1, hours=6, minutes=30),
        tense="future",
        category="life",
        color="#3FAE6A",
        raw_input="明天晚上提醒我跑步",
        confidence=0.88,
    ),
]
