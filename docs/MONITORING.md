# 监控与可观测性文档

## 概述

EmoAgent系统采用Prometheus + Grafana构建监控体系，提供实时的业务指标、性能指标和健康状态监控。本文档说明监控系统的架构、配置、使用方法和扩展方案。

## 监控架构

```
Application (FastAPI)
    ↓ /metrics endpoint
Prometheus (采集与存储)
    ↓ PromQL查询
Grafana (可视化仪表板)
```

### 技术选型

| 组件 | 版本 | 作用 | 访问地址 |
|------|------|------|---------|
| Prometheus | latest | 时序数据库，指标采集 | http://localhost:9090 |
| Grafana | latest | 数据可视化，仪表板 | http://localhost:3000 |
| prometheus-fastapi-instrumentator | >=7.0.0 | FastAPI自动化指标 | - |
| prometheus-client | >=0.20.0 | 自定义指标SDK | - |

## 指标体系

### 1. 业务指标 (Business Metrics)

| 指标名称 | 类型 | 标签 | 说明 |
|---------|------|------|------|
| `emoagent_sessions_total` | Counter | - | 会话创建总数 |
| `emoagent_messages_total` | Counter | - | 消息处理总数 |
| `emoagent_crisis_total` | Counter | category | 危机检测次数（按类别） |
| `emoagent_rating_submissions_total` | Counter | type | 自评提交总数（before/after） |
| `emoagent_rating_score` | Histogram | type | 自评分数分布 |

**使用场景**：
- 日活跃用户（DAU）计算
- 消息量趋势分析
- 危机事件监控和告警
- 用户情绪改善效果评估

### 2. 性能指标 (Performance Metrics)

| 指标名称 | 类型 | 标签 | 说明 |
|---------|------|------|------|
| `emoagent_bert_latency_seconds` | Histogram | - | BERT推理延迟 |
| `emoagent_api_latency_seconds` | Histogram | endpoint | API端点响应时间 |
| `http_requests_total` | Counter | method, status | HTTP请求统计（自动采集） |
| `http_request_duration_seconds` | Histogram | method, handler | HTTP请求延迟（自动采集） |

**使用场景**：
- 识别性能瓶颈（P95/P99延迟）
- 优化BERT推理速度
- API响应时间SLA监控

### 3. 情绪分析指标 (Emotion Metrics)

| 指标名称 | 类型 | 标签 | 说明 |
|---------|------|------|------|
| `emoagent_emotion_distribution` | Gauge | emotion | 当前情绪分布 |
| `emoagent_active_sessions` | Gauge | - | 活跃会话数 |

**情绪标签**：`sadness`, `joy`, `love`, `anger`, `fear`, `surprise`

**使用场景**：
- 用户情绪趋势分析
- 情绪分布饼图展示
- 系统负载监控

### 4. 系统健康指标 (System Health)

通过 `/health` 端点检测：
- **数据库**：PostgreSQL连接状态和查询延迟
- **缓存**：Redis连接状态和PING延迟
- **LLM服务**：DeepSeek API可用性

**响应示例**：

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "database": {"status": "up", "latency_ms": 5},
    "redis": {"status": "up", "latency_ms": 2},
    "llm": {"status": "up", "provider": "mock"}
  }
}
```

**HTTP状态码**：
- `200 OK` - 所有组件健康
- `503 Service Unavailable` - 任一组件不可用

## 快速开始

### 启动监控服务

```bash
# 1. 确保环境变量配置正确
cp .env.development .env

# 2. 启动所有服务（包括Prometheus和Grafana）
docker-compose up -d

# 3. 验证服务状态
docker-compose ps
```

### 访问监控界面

1. **Prometheus**：http://localhost:9090
   - 查询语言：PromQL
   - 查看原始指标和时序数据
   - 配置告警规则

2. **Grafana**：http://localhost:3000
   - 默认登录：`admin / admin`（首次登录后会提示修改密码）
   - 预配置仪表板：`EmoAgent - System Monitoring`
   - 支持自定义面板和告警

3. **指标端点**：http://localhost:8200/metrics
   - Prometheus文本格式
   - 实时查看当前指标值

### 健康检查

```bash
# 命令行检查
curl http://localhost:8200/health

# 使用jq格式化输出
curl -s http://localhost:8200/health | jq
```

## Grafana 仪表板

### 预配置面板

仪表板位置：`monitoring/grafana/dashboards/emoagent.json`

**面板组**：

1. **业务指标面板**：
   - 会话和消息创建速率（rate/5m）
   - 危机检测趋势（按类别分组）

2. **情绪分析面板**：
   - 情绪分布饼图（7种情绪）
   - 活跃会话数仪表盘

3. **性能指标面板**：
   - BERT推理延迟（P50/P95/P99）
   - API端点响应时间

4. **系统健康面板**：
   - HTTP状态码分布
   - 请求速率和错误率

### 自定义面板

**常用PromQL查询**：

```promql
# 每分钟消息处理速率
rate(emoagent_messages_total[1m])

# P95 BERT延迟
histogram_quantile(0.95, rate(emoagent_bert_latency_seconds_bucket[5m]))

# 按情绪统计当前分布
sum by(emotion) (emoagent_emotion_distribution)

# 危机触发率（每小时）
increase(emoagent_crisis_total[1h])

# API错误率（5xx状态码）
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### 添加新面板

1. 登录Grafana（http://localhost:3000）
2. 打开 `EmoAgent - System Monitoring` 仪表板
3. 点击右上角 `Add` → `Visualization`
4. 选择数据源：`Prometheus`
5. 编写PromQL查询
6. 选择图表类型（时间序列、饼图、仪表盘等）
7. 保存面板

## 告警配置（可选）

### Prometheus 告警规则

创建 `monitoring/prometheus/alerts.yml`：

```yaml
groups:
  - name: emoagent_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      - alert: HighBERTLatency
        expr: |
          histogram_quantile(0.95, 
            rate(emoagent_bert_latency_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "BERT inference is slow"
          description: "P95 latency is {{ $value }}s"
      
      - alert: HighCrisisRate
        expr: rate(emoagent_crisis_total[5m]) > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High crisis detection rate"
          description: "Crisis triggers: {{ $value }}/s"
```

### 集成告警通知

**方式一：Grafana Alert Manager**（推荐）
1. 在Grafana中配置通知渠道（Slack、Email、Webhook）
2. 在面板中设置告警阈值
3. 自动发送通知

**方式二：Prometheus Alert Manager**
1. 部署Alert Manager容器
2. 配置路由和接收器
3. 在Prometheus中加载告警规则

## LLMOps 监控扩展（真实LLM上线后）

### 延后实施说明

当前系统使用Mock LLM，暂不实施LLMOps监控。当切换到真实LLM（DeepSeek等）后，需补充以下内容：

### 扩展指标（+0.5天工作量）

| 指标名称 | 类型 | 标签 | 说明 |
|---------|------|------|------|
| `emoagent_llm_tokens_total` | Counter | type, provider | Token消耗（prompt/completion） |
| `emoagent_llm_cost_usd` | Counter | provider | 成本估算（美元） |
| `emoagent_llm_calls_total` | Counter | provider, status | 调用状态（success/timeout/error/fallback） |
| `emoagent_llm_retry_total` | Counter | provider | 重试次数 |
| `emoagent_llm_latency_seconds` | Histogram | provider, status | 调用延迟 |
| `emoagent_llm_response_length` | Histogram | provider | 响应长度 |

### 成本计算实现

在 `app/services/deepseek_llm_service.py` 中埋点：

```python
from app.utils.metrics import llm_tokens_total, llm_cost_usd

# 定价配置（需定期更新）
PRICING = {
    'deepseek-chat': {
        'prompt': 0.0014 / 1000,
        'completion': 0.002 / 1000
    }
}

# 在LLM调用后记录
response = await self.client.chat.completions.create(...)
prompt_tokens = response.usage.prompt_tokens
completion_tokens = response.usage.completion_tokens

llm_tokens_total.labels(type='prompt', provider='deepseek').inc(prompt_tokens)
llm_tokens_total.labels(type='completion', provider='deepseek').inc(completion_tokens)

cost = (
    prompt_tokens * PRICING['deepseek-chat']['prompt'] +
    completion_tokens * PRICING['deepseek-chat']['completion']
)
llm_cost_usd.labels(provider='deepseek').inc(cost)
```

### Grafana LLM 面板

新增面板：
- Token消耗趋势（区分prompt/completion）
- 累计成本估算（按天/周/月）
- 调用成功率（success/timeout/error/fallback占比）
- Provider对比（成本、延迟、成功率）

## 数据保留策略

### Prometheus 数据存储

默认配置：
- 保留期：15天
- 存储路径：Docker卷 `prometheus_data`

修改保留期（在 `monitoring/prometheus.yml` 中）：

```yaml
global:
  scrape_interval: 15s
  
# 添加存储配置
storage:
  retention:
    time: 30d
    size: 10GB
```

### Grafana 数据

- 仪表板配置：持久化在Docker卷 `grafana_data`
- 用户配置和权限：存储在SQLite数据库中

## 性能影响

### Prometheus 采集开销

- **CPU**：< 1% (每15秒采集一次)
- **内存**：约50MB基础 + 每天2MB时序数据
- **网络**：每次采集约10KB

### 自定义指标开销

- Counter/Gauge：微秒级，忽略不计
- Histogram：毫秒级，建议合理设置bucket

**优化建议**：
- 避免高基数标签（如：user_id、message_content）
- 合理设置抓取间隔（不建议< 10s）
- 定期清理过期数据

## 常见查询示例

### 业务分析查询

```promql
# 今日新增会话数
increase(emoagent_sessions_total[24h])

# 每小时消息量
rate(emoagent_messages_total[1h]) * 3600

# 最近1小时情绪分布
sum by(emotion) (increase(emoagent_emotion_distribution[1h]))

# 危机触发率趋势
rate(emoagent_crisis_total[5m])
```

### 性能分析查询

```promql
# BERT平均延迟
rate(emoagent_bert_latency_seconds_sum[5m]) / rate(emoagent_bert_latency_seconds_count[5m])

# API P99延迟（按端点）
histogram_quantile(0.99, sum by(le, endpoint) (rate(emoagent_api_latency_seconds_bucket[5m])))

# 慢请求数（>5秒）
sum(increase(emoagent_api_latency_seconds_bucket{le="5.0"}[5m]))
```

### 健康状态查询

```promql
# HTTP请求成功率
sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m]))

# 错误率
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# 当前活跃会话数
emoagent_active_sessions
```

## 故障排查

### 问题1：Prometheus无法采集指标

**症状**：Grafana显示"No data"

**排查步骤**：
```bash
# 1. 检查backend /metrics端点
curl http://localhost:8200/metrics

# 2. 检查Prometheus targets状态
# 访问 http://localhost:9090/targets
# 确认backend目标状态为"UP"

# 3. 检查Prometheus日志
docker logs emoagent-prometheus

# 4. 验证网络连接
docker exec emoagent-prometheus ping backend
```

**常见原因**：
- `ENABLE_METRICS=false`（检查环境变量）
- 端口映射错误（确认8200:8000）
- Prometheus配置文件错误（检查 `monitoring/prometheus.yml`）

### 问题2：Grafana无法连接Prometheus

**症状**：Grafana显示"Data source error"

**排查步骤**：
```bash
# 1. 检查Prometheus服务状态
docker ps | grep prometheus

# 2. 测试Prometheus API
curl http://localhost:9090/api/v1/query?query=up

# 3. 检查Grafana数据源配置
# 访问 http://localhost:3000/datasources
# 确认URL为 http://prometheus:9090
```

### 问题3：指标值异常

**症状**：指标值为0或不增长

**排查步骤**：
```bash
# 1. 检查应用日志
docker logs emoagent-backend | grep -i error

# 2. 验证指标是否被调用
# 在代码中添加日志：
# logger.info("Incrementing sessions_total")
# sessions_total.inc()

# 3. 使用Prometheus查询验证
# 访问 http://localhost:9090/graph
# 查询: emoagent_sessions_total
```

## 最佳实践

### 1. 指标设计原则

**应该做**：
- 使用有意义的指标名称（前缀：`emoagent_`）
- 合理选择指标类型（Counter/Gauge/Histogram）
- 添加必要的标签（便于多维度分析）

**不应该做**：
- 记录用户敏感信息（消息内容、session_id等）
- 使用高基数标签（会爆炸存储空间）
- 过度采集（每秒采集无意义）

### 2. 仪表板设计

- 按业务域分组（业务、性能、健康）
- 使用合适的时间窗口（5m/1h/24h）
- 添加阈值线（如：P95延迟< 2s）
- 配置自动刷新（建议10s-30s）

### 3. 告警设置

**关键告警**：
- 错误率 > 5%（持续5分钟）
- P95延迟 > 2秒（持续5分钟）
- 危机触发率异常（突增10倍）
- 数据库/Redis不可用

**告警疲劳预防**：
- 设置合理的`for`持续时间（避免抖动）
- 使用告警分组和抑制
- 区分严重级别（critical/warning/info）

## 监控数据导出

### 导出 Prometheus 数据

```bash
# 使用 promtool 导出时间范围数据
promtool tsdb dump /prometheus --min-time=2026-01-01T00:00:00Z --max-time=2026-01-31T23:59:59Z

# 使用 HTTP API 导出
curl 'http://localhost:9090/api/v1/query_range?query=emoagent_sessions_total&start=2026-01-01T00:00:00Z&end=2026-01-31T23:59:59Z&step=1h' | jq > data.json
```

### 导出 Grafana 仪表板

```bash
# 方式一：使用Grafana UI
# Dashboard → Share → Export → Save to file

# 方式二：使用API
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/dashboards/uid/emoagent-main \
  | jq '.dashboard' > dashboard.json
```

## 扩展方案

### 阶段二：专业 LLMOps 平台（可选）

**升级时机**：
- 日LLM调用量 > 10,000次
- 需要完整调用链路追踪（trace）
- 需要Prompt版本管理和A/B测试

**推荐工具**：

| 工具 | 开源 | 自托管 | 特点 |
|------|------|--------|------|
| LangFuse | ✅ | ✅ | 开源、隐私友好、功能全面 |
| LangSmith | ❌ | ❌ | LangChain官方、trace完善 |
| Helicone | ❌ | ❌ | 专注成本优化、缓存功能强 |

**集成工作量**：+2天

### 阶段三：日志聚合（可选）

**工具选择**：
- ELK Stack（Elasticsearch + Logstash + Kibana）
- Grafana Loki（轻量级，与Grafana集成）

**适用场景**：
- 需要全文搜索日志
- 多服务日志集中查询
- 调试复杂问题

## 监控数据安全

### 访问控制

1. **Prometheus**：
   - 默认无认证（仅内网访问）
   - 生产环境建议配置基础认证或反向代理

2. **Grafana**：
   - 默认用户名/密码：admin/admin
   - 生产环境务必修改密码（环境变量 `GRAFANA_PASSWORD`）
   - 支持LDAP、OAuth等企业认证

### 数据隐私

**指标采集原则**：
- ❌ 不记录用户消息内容
- ❌ 不记录session_id（高基数）
- ✅ 仅统计聚合数据（计数、延迟、分布）

**日志脱敏**：
- 已在 `app/utils/logging.py` 中配置结构化日志
- 避免记录用户敏感信息到日志

## 相关文档

- [系统架构](ARCHITECTURE.md) - 整体架构设计
- [部署文档](DEPLOYMENT.md) - Docker部署和环境配置
- [开发指南](DEVELOPMENT.md) - 本地开发环境
- [Prometheus官方文档](https://prometheus.io/docs/)
- [Grafana官方文档](https://grafana.com/docs/)

## 常见问题 (FAQ)

### Q1: 如何重置Grafana密码？

```bash
# 使用docker exec进入容器
docker exec -it emoagent-grafana grafana-cli admin reset-admin-password newpassword
```

### Q2: 如何备份监控数据？

```bash
# 备份Prometheus数据
docker run --rm -v emoagent-v1_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# 备份Grafana配置
docker run --rm -v emoagent-v1_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

### Q3: 监控系统占用多少资源？

**典型资源占用**（Docker环境）：
- Prometheus：内存200MB，CPU 1-2%
- Grafana：内存150MB，CPU 1%
- Backend额外开销：内存+10MB，CPU +0.5%

**总计**：约350MB内存，对8GB系统影响可忽略

### Q4: 如何禁用监控？

```bash
# 方式一：环境变量
echo "ENABLE_METRICS=false" >> .env
docker-compose restart backend

# 方式二：停止监控服务
docker-compose stop prometheus grafana
```

## 待补充内容

- [ ] 性能压测和容量规划
- [ ] 分布式追踪（Jaeger/Zipkin集成）
- [ ] 日志聚合方案（ELK Stack）
- [ ] 专业LLMOps平台集成（LangFuse等）
- [ ] 自定义告警规则库
- [ ] 监控数据归档方案

---

**文档版本**: v0.1.0  
**最后更新**: 2026-03-13  
**维护者**: 后端团队
