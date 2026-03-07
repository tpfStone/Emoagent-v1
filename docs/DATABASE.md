# 数据库文档

## 概述

本文档详细描述情绪对话系统的数据库设计，包括表结构、索引、关系和迁移管理。

**数据库管理系统**: PostgreSQL 16+  
**ORM 框架**: SQLAlchemy 2.0  
**迁移工具**: Alembic

---

## 表结构设计

### 1. sessions 表

**用途**: 管理匿名会话的基本信息


| 字段名            | 数据类型         | 约束              | 默认值   | 说明        |
| -------------- | ------------ | --------------- | ----- | --------- |
| id             | SERIAL       | PRIMARY KEY     | -     | 自增主键      |
| session_id     | UUID         | UNIQUE NOT NULL | -     | 会话唯一标识符   |
| token          | VARCHAR(255) | NOT NULL        | -     | 匿名访问token |
| created_at     | TIMESTAMP    | NOT NULL        | NOW() | 创建时间      |
| last_active_at | TIMESTAMP    | NOT NULL        | NOW() | 最后活跃时间    |


**索引**:

```sql
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_last_active ON sessions(last_active_at DESC);
```

**SQLAlchemy 模型**:

```python
class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    conversations = relationship("Conversation", back_populates="session")
    turns = relationship("Turn", back_populates="session")
    ratings = relationship("UserRating", back_populates="session")
```

---

### 2. conversations 表

> **⚠️ 阶段1状态：仅建表，不编写 DAO/Service 业务代码。**
>
> 当前阶段1为 1 session = 1 conversation，`turns` 表已通过 `session_id` 直接关联会话，
> `turn_count` 可由 `SELECT COUNT(*) FROM turns WHERE session_id = ?` 动态获取，
> 因此本表在阶段1中不参与任何业务流程。保留此表是为未来扩展预留。
>
> **未来可实现方向：**
> - **多对话支持**：一个 session（用户）可发起多次独立对话（如上午、下午各一次），
>   结构变为 `session 1:N conversation 1:N turn`，此时本表承担对话级别的元信息管理。
> - **长期记忆**：基于 conversation 粒度做对话摘要存储，支持跨会话的个性化记忆召回。
> - **对话归档**：为历史对话提供归档、标题、标签等管理能力。

**用途**: 记录每个会话的对话元信息


| 字段名        | 数据类型      | 约束          | 默认值   | 说明                     |
| ---------- | --------- | ----------- | ----- | ---------------------- |
| id         | SERIAL    | PRIMARY KEY | -     | 自增主键                   |
| session_id | UUID      | FOREIGN KEY | -     | 关联 sessions.session_id |
| turn_count | INTEGER   | NOT NULL    | 0     | 总轮数                    |
| created_at | TIMESTAMP | NOT NULL    | NOW() | 创建时间                   |
| updated_at | TIMESTAMP | NOT NULL    | NOW() | 更新时间                   |


**外键约束**:

```sql
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
```

**索引**:

```sql
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

**SQLAlchemy 模型**:

```python
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False)
    turn_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    session = relationship("Session", back_populates="conversations")
```

---

### 3. turns 表（核心指标表）

**用途**: 存储每轮对话的详细信息和性能指标


| 字段名               | 数据类型        | 约束          | 默认值   | 说明                     |
| ----------------- | ----------- | ----------- | ----- | ---------------------- |
| id                | SERIAL      | PRIMARY KEY | -     | 自增主键                   |
| session_id        | UUID        | FOREIGN KEY | -     | 关联 sessions.session_id |
| turn_index        | INTEGER     | NOT NULL    | -     | 第几轮（从1开始）              |
| user_message      | TEXT        | NOT NULL    | -     | 用户输入原文                 |
| assistant_message | TEXT        | NOT NULL    | -     | AI回复原文                 |
| emotion_label     | VARCHAR(50) | NULL        | -     | 情绪标签                   |
| is_crisis         | BOOLEAN     | NOT NULL    | FALSE | 是否触发危机干预               |
| bert_latency_ms   | INTEGER     | NULL        | -     | BERT推理耗时（毫秒）           |
| llm_latency_ms    | INTEGER     | NULL        | -     | LLM调用耗时（毫秒）            |
| created_at        | TIMESTAMP   | NOT NULL    | NOW() | 创建时间                   |


**外键约束**:

```sql
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
```

**索引**:

```sql
CREATE INDEX idx_turns_session_id ON turns(session_id);
CREATE INDEX idx_turns_created_at ON turns(created_at DESC);
CREATE INDEX idx_turns_is_crisis ON turns(is_crisis) WHERE is_crisis = TRUE;
CREATE INDEX idx_turns_emotion_label ON turns(emotion_label);
CREATE INDEX idx_turns_composite ON turns(session_id, turn_index);
```

**SQLAlchemy 模型**:

```python
class Turn(Base):
    __tablename__ = 'turns'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False)
    turn_index = Column(Integer, nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    emotion_label = Column(String(50), nullable=True)
    is_crisis = Column(Boolean, nullable=False, default=False)
    bert_latency_ms = Column(Integer, nullable=True)
    llm_latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    session = relationship("Session", back_populates="turns")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('session_id', 'turn_index', name='uq_session_turn'),
    )
```

---

### 4. crisis_rules 表

**用途**: 存储危机关键词及对应的干预话术


| 字段名               | 数据类型         | 约束          | 默认值   | 说明           |
| ----------------- | ------------ | ----------- | ----- | ------------ |
| id                | SERIAL       | PRIMARY KEY | -     | 自增主键         |
| keyword           | VARCHAR(255) | NOT NULL    | -     | 危机关键词（支持正则）  |
| response_template | TEXT         | NOT NULL    | -     | 固定回复话术       |
| priority          | INTEGER      | NOT NULL    | 0     | 优先级（数值越大越优先） |
| enabled           | BOOLEAN      | NOT NULL    | TRUE  | 是否启用         |
| created_at        | TIMESTAMP    | NOT NULL    | NOW() | 创建时间         |
| updated_at        | TIMESTAMP    | NOT NULL    | NOW() | 更新时间         |


**索引**:

```sql
CREATE INDEX idx_crisis_enabled_priority ON crisis_rules(enabled, priority DESC);
```

**SQLAlchemy 模型**:

```python
class CrisisRule(Base):
    __tablename__ = 'crisis_rules'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(255), nullable=False)
    response_template = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False, default=0)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### 5. user_ratings 表

**用途**: 存储用户的前后自评数据


| 字段名         | 数据类型        | 约束              | 默认值   | 说明                     |
| ----------- | ----------- | --------------- | ----- | ---------------------- |
| id          | SERIAL      | PRIMARY KEY     | -     | 自增主键                   |
| session_id  | UUID        | FOREIGN KEY     | -     | 关联 sessions.session_id |
| rating_type | VARCHAR(10) | NOT NULL        | -     | 'before' 或 'after'     |
| score       | INTEGER     | NOT NULL, CHECK | -     | 评分1-10                 |
| created_at  | TIMESTAMP   | NOT NULL        | NOW() | 创建时间                   |


**外键约束**:

```sql
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
```

**检查约束**:

```sql
CHECK (score >= 1 AND score <= 10)
CHECK (rating_type IN ('before', 'after'))
```

**索引**:

```sql
CREATE INDEX idx_ratings_session_id ON user_ratings(session_id);
CREATE INDEX idx_ratings_type ON user_ratings(rating_type);
```

**SQLAlchemy 模型**:

```python
class UserRating(Base):
    __tablename__ = 'user_ratings'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False)
    rating_type = Column(Enum('before', 'after', name='rating_type_enum'), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    session = relationship("Session", back_populates="ratings")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint('score >= 1 AND score <= 10', name='check_score_range'),
    )
```

---

## 表关系图（ERD）

```mermaid
erDiagram
    SESSIONS ||--o{ CONVERSATIONS : has
    SESSIONS ||--o{ TURNS : has
    SESSIONS ||--o{ USER_RATINGS : has
    
    SESSIONS {
        int id PK
        uuid session_id UK
        varchar token
        timestamp created_at
        timestamp last_active_at
    }
    
    CONVERSATIONS {
        int id PK
        uuid session_id FK
        int turn_count
        timestamp created_at
        timestamp updated_at
        string _note "阶段1仅建表-未来扩展用"
    }
    
    TURNS {
        int id PK
        uuid session_id FK
        int turn_index
        text user_message
        text assistant_message
        varchar emotion_label
        boolean is_crisis
        int bert_latency_ms
        int llm_latency_ms
        timestamp created_at
    }
    
    CRISIS_RULES {
        int id PK
        varchar keyword
        text response_template
        int priority
        boolean enabled
        timestamp created_at
        timestamp updated_at
    }
    
    USER_RATINGS {
        int id PK
        uuid session_id FK
        varchar rating_type
        int score
        timestamp created_at
    }
```



---

## 数据迁移（用于版本变更）

### Alembic 配置

**初始化 Alembic**:

```bash
alembic init alembic
```

**配置文件** (`alembic.ini`):

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost:5432/emoagent
```

**环境配置** (`alembic/env.py`):

> **注意**：`.env` 中 `DATABASE_URL` 使用 `postgresql://` 格式（Alembic 迁移使用同步驱动），
> 应用层 `database.py` 在创建异步引擎时自动将其转换为 `postgresql+asyncpg://`。

```python
import os
from dotenv import load_dotenv
from app.database import Base
from app.models.models import *

load_dotenv()

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata
```

### 创建迁移

```bash
# 自动生成迁移（推荐）
alembic revision --autogenerate -m "Create initial tables"

# 手动创建迁移
alembic revision -m "Add new column"
```

### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级一个版本
alembic upgrade +1

# 降级一个版本
alembic downgrade -1

# 降级到特定版本
alembic downgrade <revision_id>

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

### 迁移示例

```python
# alembic/versions/001_create_initial_tables.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # 创建 sessions 表
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_active_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    
    # 创建索引
    op.create_index('idx_sessions_session_id', 'sessions', ['session_id'])
    op.create_index('idx_sessions_token', 'sessions', ['token'])

def downgrade():
    op.drop_index('idx_sessions_token')
    op.drop_index('idx_sessions_session_id')
    op.drop_table('sessions')
```

---

## 数据字典

### sessions

- **session_id**: UUID v4 格式，作为会话的全局唯一标识
- **token**: 用于 API 认证的令牌，随机生成
- **last_active_at**: 每次 API 调用时更新，用于追踪活跃会话

### turns

- **turn_index**: 从 1 开始，标识对话的第几轮
- **emotion_label**: 可能的值包括：sadness, joy, love, anger, fear, surprise（nateraw/bert-base-uncased-emotion 模型输出）
- **is_crisis**: 当用户消息匹配危机关键词时设为 TRUE
- **bert_latency_ms/llm_latency_ms**: 用于性能监控和优化

### crisis_rules

- **keyword**: 支持正则表达式，如 `(自杀|轻生|想死)`
- **priority**: 值越大优先级越高，匹配时按优先级降序检查
- **enabled**: 可临时禁用某条规则而不删除

### user_ratings

- **rating_type**: 'before' 表示会话开始前自评，'after' 表示会话结束后自评
- **score**: 1-10 的整数，用于评估情绪改善程度

---

## 性能优化

### 索引策略

1. **高频查询字段建索引**:
  - `sessions.session_id` (查询会话)
  - `turns.session_id` (查询对话历史)
  - `turns.created_at` (时间范围查询)
2. **组合索引**:
  - `(session_id, turn_index)` 加速按会话查询特定轮次
3. **部分索引**:
  - `WHERE is_crisis = TRUE` 仅索引危机记录，节省空间

### 查询优化

**常用查询示例**:

```sql
-- 获取某会话的最近 N 轮对话
SELECT * FROM turns
WHERE session_id = :session_id
ORDER BY turn_index DESC
LIMIT 6;

-- 统计情绪分布
SELECT emotion_label, COUNT(*) as count
FROM turns
WHERE session_id = :session_id
  AND emotion_label IS NOT NULL
GROUP BY emotion_label;

-- 查询危机会话数量
SELECT COUNT(DISTINCT session_id)
FROM turns
WHERE is_crisis = TRUE
  AND created_at >= NOW() - INTERVAL '7 days';
```

### 分区（可选，数据量大时）

```sql
-- 按时间分区 turns 表
CREATE TABLE turns_2026_03 PARTITION OF turns
FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

---

## 数据维护

### 定期清理

**清理过期会话**:

```sql
-- 删除 30 天未活跃的会话及其关联数据
DELETE FROM sessions
WHERE last_active_at < NOW() - INTERVAL '30 days';
-- 级联删除会自动清理 conversations, turns, user_ratings
```

### 数据归档

**归档历史数据**:

```sql
-- 将旧数据移动到归档表
INSERT INTO turns_archive
SELECT * FROM turns
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM turns
WHERE created_at < NOW() - INTERVAL '1 year';
```

### VACUUM 和 ANALYZE

```sql
-- 回收空间并更新统计信息
VACUUM ANALYZE sessions;
VACUUM ANALYZE turns;
```

---

## 备份与恢复

### 备份策略

**全量备份**:

```bash
pg_dump -U emoagent_user -F c -b -v -f backup_$(date +%Y%m%d).backup emoagent
```

**增量备份（使用 WAL 归档）**:

```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

### 恢复数据库

```bash
# 从全量备份恢复
pg_restore -U emoagent_user -d emoagent -c backup_20260301.backup

# 恢复到特定时间点（PITR）
pg_restore -U emoagent_user -d emoagent -T '2026-03-01 12:00:00'
```

---

## 安全配置

1. **最小权限原则**:
  ```sql
   -- 创建只读用户
   CREATE USER readonly_user WITH PASSWORD 'xxx';
   GRANT CONNECT ON DATABASE emoagent TO readonly_user;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
  ```
2. **敏感数据加密**:
  - 使用 pgcrypto 扩展加密敏感字段
  - 在应用层加密后再存储
3. **SQL 注入防护**:
  - 使用 SQLAlchemy ORM 自动防护
  - 避免拼接 SQL 字符串

### 数据库安全职责

- **后端团队**：负责数据库权限管理、SQL注入防护、数据加密实施

---

## 待补充内容

- 读写分离配置（主从复制）
- 连接池优化（PgBouncer）
- 数据库监控指标
- 慢查询分析
- 数据加密方案
- 高可用方案（Patroni/Replication）

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-02  
**维护者**: 后端团队（2人）