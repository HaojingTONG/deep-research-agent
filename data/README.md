# Deep Research Agent - Data Directory Structure

## 🎯 目录约定与数据契约

这个目录结构设计用于支持可回放、可评测、可观测的深度研究工作流。

## 📁 目录结构详解

```
data/
├─ README.md                           # 目录约定与数据契约说明
├─ out/                                # 最终导出报告和结果
├─ runs/                               # 每次运行的可回放快照
│  └─ 2025-09-21_17-30-12/             # run_id（时间戳）
│     ├─ clarify.json                  # Phase 1: 澄清结果
│     ├─ brief.md                      # Phase 2: 研究大纲
│     ├─ plan.json                     # Phase 3: 搜索计划
│     ├─ evidence.jsonl                # Phase 4: 逐条evidence（JSON Lines）
│     ├─ compressed.json               # Phase 5: 压缩结果
│     ├─ report.md                     # Phase 6: 最终报告
│     ├─ judge.json                    # Phase 7: 质量评估
│     ├─ replan.json                   # Phase 8: 恢复计划
│     └─ logs.ndjson                   # Phase 10: 观测日志（每行一个事件）
├─ seeds/                              # 题库/受众/约束（用于批量实验）
│  ├─ queries.jsonl                    # 研究问题清单（JSONL）
│  ├─ audiences.yaml                   # 目标读者画像（exec/engineer等）
│  └─ constraints.yaml                 # 时间窗/地域/输出要求等
├─ web_cache/                          # 检索与抓取缓存（加速/可复现）
│  ├─ search/                          # 搜索结果缓存（JSONL）
│  └─ fetch/                           # 原始网页（HTML或TXT）
├─ evidence/                           # 从原始网页抽取的证据块
│  ├─ blocks.jsonl                     # 结构化证据（url/title/quote等）
│  └─ map.csv                          # evidence ↔ run ↔ 段落 映射表
├─ compressed/                         # 聚合/去重/冲突对齐后的产物
│  └─ notes.json
├─ corpus/                             # 可选：离线语料（pdf/txt）与清洗文本
│  ├─ raw/                             # 原始上传
│  └─ clean/                           # 清洗后的纯文本/分段
├─ rag_index/                          # 可选：向量索引或BM25索引
│  └─ chroma/                          # 例如Chroma目录
├─ eval/                               # 评测任务、金标与运行结果
│  ├─ tasks.jsonl                      # 评测题（输入/预期要点）
│  ├─ gold/                            # 参考要点/必须引用的来源
│  │  ├─ answers.md
│  │  └─ citations.jsonl
│  └─ runs/
│     └─ 2025-09-21_17-30-12/          # 针对一次run的评测输出
│        ├─ metrics.json
│        └─ coverage.csv
├─ observability/                      # 运行可观测数据的长期汇聚
│  ├─ traces.ndjson                    # 轨迹（节点级I/O摘要）
│  └─ errors.ndjson                    # 异常栈、重试原因
├─ whitelist/                          # 来源白名单（提升可信度）
│  └─ domains.txt
└─ blacklist/                          # 垃圾源/聚合站黑名单
   └─ domains.txt
```

## 🏷️ 文件格式规范

### Run Files (data/runs/YYYYMMDD_HHMMSS/)
- `clarify.json` - 结构化澄清结果
- `brief.md` - Markdown格式研究大纲
- `plan.json` - 搜索计划和任务分解
- `evidence.jsonl` - JSON Lines格式证据记录
- `compressed.json` - 压缩和冲突分析结果
- `report.md` - 最终研究报告
- `judge.json` - 质量评估和打分
- `replan.json` - 恢复和重计划方案
- `logs.ndjson` - 结构化运行日志

### Evidence Format (evidence.jsonl)
```json
{"url": "...", "title": "...", "content": "...", "score": 4.2, "timestamp": "..."}
{"url": "...", "title": "...", "content": "...", "score": 3.8, "timestamp": "..."}
```

### Logs Format (logs.ndjson)
```json
{"timestamp": "2025-09-21T17:30:12Z", "phase": "clarify", "action": "start", "data": {...}}
{"timestamp": "2025-09-21T17:30:15Z", "phase": "clarify", "action": "complete", "data": {...}}
```

## 🔄 数据流转

1. **输入**: 用户查询 → `runs/{timestamp}/`
2. **处理**: 各阶段输出 → 对应的文件
3. **缓存**: 网页抓取 → `web_cache/`
4. **聚合**: 证据提取 → `evidence/`
5. **输出**: 最终报告 → `out/` + `runs/{timestamp}/report.md`
6. **监控**: 运行日志 → `observability/`

## 🎯 使用说明

### 基础运行
```bash
python main.py "你的研究问题"
# 输出会保存到 data/runs/{timestamp}/ 和 data/out/
```

### 批量实验
```bash
# 使用seeds中的问题批量运行
python batch_run.py --queries data/seeds/queries.jsonl
```

### 评测运行
```bash
# 针对特定run进行评测
python evaluate.py --run-id 20250921_173012
```

这个结构支持完整的研究工作流程，包括缓存、评测和长期观测。