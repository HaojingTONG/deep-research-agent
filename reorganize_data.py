#!/usr/bin/env python3
"""
重新组织data目录结构
"""

import os
import shutil
import glob
from datetime import datetime

def create_new_structure():
    """创建新的目录结构"""

    # 新的目录结构
    new_structure = {
        "data/runs": "按运行批次组织的完整研究会话",
        "data/runs/YYYYMMDD_HHMMSS": "单次完整研究运行的所有文件",
        "data/archive": "历史和归档文件",
        "data/archive/YYYY-MM": "按月归档的旧文件",
        "data/config": "配置和模板文件",
        "data/config/templates": "Jinja2模板文件",
        "data/config/schemas": "JSON Schema验证文件",
        "data/monitoring": "系统监控和可观测性",
        "data/monitoring/audit": "审计追踪报告",
        "data/monitoring/metrics": "性能指标和统计",
        "data/monitoring/errors": "错误日志和异常报告",
        "data/temp": "临时和测试文件",
        "data/temp/tests": "测试运行产生的文件",
        "data/temp/demos": "演示和示例文件"
    }

    # 创建目录结构
    print("📁 创建新的目录结构...")
    for path, description in new_structure.items():
        if not path.endswith("YYYY-MM") and not path.endswith("YYYYMMDD_HHMMSS"):
            os.makedirs(path, exist_ok=True)
            print(f"   ✓ {path} - {description}")

    # 创建示例运行目录
    sample_run = f"data/runs/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(sample_run, exist_ok=True)
    print(f"   ✓ {sample_run} - 示例运行目录")

    # 创建示例归档目录
    sample_archive = f"data/archive/{datetime.now().strftime('%Y-%m')}"
    os.makedirs(sample_archive, exist_ok=True)
    print(f"   ✓ {sample_archive} - 示例归档目录")

def migrate_existing_files():
    """迁移现有文件到新结构"""

    print("\n📦 迁移现有文件...")

    # 迁移计划
    migrations = [
        # 配置和模板文件
        ("data/templates/*", "data/config/templates/"),
        ("data/README.md", "data/config/"),

        # 监控和日志文件
        ("data/logs/audit_trail_*", "data/monitoring/audit/"),

        # 临时和测试文件 (识别模式)
        ("data/*/.*demo*", "data/temp/demos/"),
        ("data/*/.*test*", "data/temp/tests/"),

        # 其他文件移到temp (稍后手动整理)
        ("data/evaluations/*", "data/temp/"),
        ("data/evidence/*", "data/temp/"),
        ("data/intermediate/*", "data/temp/"),
        ("data/reports/*", "data/temp/"),
    ]

    for pattern, destination in migrations:
        source_files = glob.glob(pattern, recursive=True)
        if source_files:
            os.makedirs(destination, exist_ok=True)
            for file_path in source_files:
                if os.path.isfile(file_path):
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(destination, filename)
                    try:
                        shutil.move(file_path, dest_path)
                        print(f"   ✓ {file_path} → {dest_path}")
                    except Exception as e:
                        print(f"   ⚠ {file_path} 迁移失败: {e}")

def create_documentation():
    """创建新的目录文档"""

    doc_content = """# Deep Research Agent - Data Directory Structure

## 🎯 目录设计原则

1. **按功能分组**: 不同类型的文件放在功能相关的目录中
2. **按时间组织**: 运行文件按时间戳组织，便于追踪和清理
3. **分离关注点**: 配置、监控、临时文件分别管理
4. **易于归档**: 支持定期归档和清理历史文件

## 📁 目录结构详解

```
data/
├── runs/                           # 研究运行文件 (按批次组织)
│   ├── 20250921_191500/           # 单次完整研究运行
│   │   ├── 01_clarified.json      # Phase 1: 澄清结果
│   │   ├── 02_brief.md             # Phase 2: 研究大纲
│   │   ├── 03_plan.json            # Phase 3: 搜索计划
│   │   ├── 04_evidence.json       # Phase 4: 证据收集
│   │   ├── 05_compressed.json     # Phase 5: 证据压缩
│   │   ├── 06_report.md            # Phase 6: 最终报告
│   │   ├── 07_evaluation.json     # Phase 7: 质量评估
│   │   ├── 08_recovery.json       # Phase 8: 恢复计划 (如需要)
│   │   ├── 09_routing.json        # Phase 9: 模型路由
│   │   ├── 10_audit.md             # Phase 10: 审计追踪
│   │   └── meta.json               # 运行元数据
│   └── 20250922_093000/           # 另一次运行
├── archive/                        # 历史归档文件
│   ├── 2025-09/                   # 按月归档
│   │   ├── completed_runs/        # 已完成的运行
│   │   ├── reports/               # 历史报告
│   │   └── evaluations/           # 历史评估
│   └── 2025-08/
├── config/                         # 配置和模板
│   ├── templates/                 # Jinja2模板文件
│   │   ├── report.md.j2           # 报告模板
│   │   ├── brief.md.j2            # 大纲模板
│   │   └── audit.md.j2            # 审计模板
│   ├── schemas/                   # JSON Schema验证
│   │   ├── clarified.schema.json  # 澄清结果Schema
│   │   ├── evidence.schema.json   # 证据格式Schema
│   │   └── evaluation.schema.json # 评估格式Schema
│   ├── settings.json              # 系统配置设置
│   └── README.md                  # 目录说明文档
├── monitoring/                     # 系统监控和可观测性
│   ├── audit/                     # 审计追踪
│   │   ├── audit_YYYYMMDD_HHMMSS.md # 运行审计报告
│   │   └── summary_YYYY-MM.md     # 月度审计汇总
│   ├── metrics/                   # 性能指标
│   │   ├── performance_YYYY-MM.json # 月度性能指标
│   │   ├── quality_trends.json    # 质量趋势分析
│   │   └── usage_stats.json       # 使用统计
│   └── errors/                    # 错误和异常
│       ├── error_log_YYYY-MM.json # 月度错误日志
│       └── recovery_analysis.json # 恢复分析报告
└── temp/                          # 临时和测试文件
    ├── tests/                     # 测试运行文件
    │   ├── test_researcher_*.json
    │   ├── test_compress_*.json
    │   └── test_*_output.*
    ├── demos/                     # 演示和示例
    │   ├── demo_report_*.md
    │   ├── sample_evidence.json
    │   └── example_*.json
    └── scratch/                   # 临时工作文件
        ├── debug_*.log
        └── temp_*.json
```

## 🏷️ 文件命名规范

### 运行文件 (data/runs/YYYYMMDD_HHMMSS/)
- `01_clarified.json` - Phase 1澄清结果
- `02_brief.md` - Phase 2研究大纲
- `03_plan.json` - Phase 3搜索计划
- `04_evidence.json` - Phase 4证据收集
- `05_compressed.json` - Phase 5证据压缩
- `06_report.md` - Phase 6最终报告
- `07_evaluation.json` - Phase 7质量评估
- `08_recovery.json` - Phase 8恢复计划 (可选)
- `09_routing.json` - Phase 9模型路由
- `10_audit.md` - Phase 10审计追踪
- `meta.json` - 运行元数据和配置

### 监控文件
- `audit_20250921_191500.md` - 特定运行的审计报告
- `performance_2025-09.json` - 月度性能统计
- `error_log_2025-09.json` - 月度错误汇总

### 临时文件
- `test_*_20250921_191500.*` - 测试文件 (带时间戳)
- `demo_*_sample.*` - 演示文件
- `debug_*.log` - 调试日志

## 🔄 文件生命周期

1. **生成**: 新文件在 `data/runs/YYYYMMDD_HHMMSS/` 中创建
2. **使用**: 运行期间的活跃文件
3. **归档**: 定期移动到 `data/archive/YYYY-MM/`
4. **清理**: 超过保留期的文件可以删除

## 🛠️ 维护操作

### 创建新运行目录
```bash
mkdir data/runs/$(date +%Y%m%d_%H%M%S)
```

### 归档旧文件 (保留最近30天)
```bash
find data/runs -type d -mtime +30 -exec mv {} data/archive/$(date +%Y-%m)/ \\;
```

### 清理临时文件
```bash
find data/temp -name "*.log" -mtime +7 -delete
find data/temp -name "debug_*" -mtime +3 -delete
```

### 生成月度报告
```bash
python -m tools.generate_monthly_summary data/archive/2025-09/
```

## 📊 目录大小管理

- `runs/`: 当前活跃运行 (建议保留最近30天)
- `archive/`: 历史文件 (按需保留，建议6个月)
- `temp/`: 临时文件 (建议7天内清理)
- `monitoring/`: 监控数据 (建议保留1年)
- `config/`: 配置文件 (永久保留)

## 🎯 使用建议

1. **日常开发**: 主要使用 `runs/` 目录
2. **调试测试**: 使用 `temp/tests/` 目录
3. **演示展示**: 使用 `temp/demos/` 目录
4. **性能分析**: 查看 `monitoring/metrics/` 目录
5. **问题排查**: 检查 `monitoring/errors/` 目录
6. **历史追溯**: 搜索 `archive/` 目录

这个结构支持高效的开发、调试、监控和维护工作流程。
"""

    with open("data/config/README.md", 'w', encoding='utf-8') as f:
        f.write(doc_content)

    print(f"\n📚 文档已创建: data/config/README.md")

def create_helper_scripts():
    """创建辅助脚本"""

    # 创建运行管理脚本
    run_manager_script = '''#!/usr/bin/env python3
"""
运行管理工具
"""

import os
import json
import shutil
from datetime import datetime, timedelta

def create_new_run():
    """创建新的运行目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"data/runs/{timestamp}"
    os.makedirs(run_dir, exist_ok=True)

    # 创建元数据文件
    meta = {
        "created": datetime.now().isoformat(),
        "status": "initialized",
        "phases": {},
        "files": [],
        "query": ""
    }

    with open(f"{run_dir}/meta.json", 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"✓ 创建新运行目录: {run_dir}")
    return run_dir

def archive_old_runs(days=30):
    """归档旧的运行文件"""
    cutoff_date = datetime.now() - timedelta(days=days)
    runs_dir = "data/runs"
    archive_dir = f"data/archive/{datetime.now().strftime('%Y-%m')}"

    os.makedirs(archive_dir, exist_ok=True)

    archived_count = 0
    for run_name in os.listdir(runs_dir):
        run_path = os.path.join(runs_dir, run_name)
        if os.path.isdir(run_path):
            # 解析时间戳
            try:
                run_time = datetime.strptime(run_name, "%Y%m%d_%H%M%S")
                if run_time < cutoff_date:
                    dest_path = os.path.join(archive_dir, run_name)
                    shutil.move(run_path, dest_path)
                    print(f"✓ 归档: {run_name}")
                    archived_count += 1
            except ValueError:
                continue

    print(f"✓ 共归档 {archived_count} 个运行目录")

def cleanup_temp_files(days=7):
    """清理临时文件"""
    cutoff_date = datetime.now() - timedelta(days=days)
    temp_dir = "data/temp"

    cleaned_count = 0
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                os.remove(file_path)
                cleaned_count += 1

    print(f"✓ 清理了 {cleaned_count} 个临时文件")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "new":
            create_new_run()
        elif sys.argv[1] == "archive":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            archive_old_runs(days)
        elif sys.argv[1] == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            cleanup_temp_files(days)
    else:
        print("用法: python run_manager.py [new|archive|cleanup] [days]")
'''

    with open("data/config/run_manager.py", 'w', encoding='utf-8') as f:
        f.write(run_manager_script)

    print(f"📜 创建管理脚本: data/config/run_manager.py")

def update_main_py():
    """更新main.py以使用新的目录结构"""

    print("\n🔧 需要手动更新main.py中的文件路径...")
    print("将以下路径模式更新为新结构:")
    print("  旧: data/reports/research_report_{timestamp}.md")
    print("  新: data/runs/{timestamp}/06_report.md")
    print("  ")
    print("  旧: data/evaluations/evaluation_{timestamp}.json")
    print("  新: data/runs/{timestamp}/07_evaluation.json")
    print("  ")
    print("  旧: data/intermediate/compression_{timestamp}.json")
    print("  新: data/runs/{timestamp}/05_compressed.json")

def main():
    """主重组函数"""

    print("🔄 重新组织Data目录结构")
    print("="*60)

    # 1. 创建新结构
    create_new_structure()

    # 2. 迁移现有文件
    migrate_existing_files()

    # 3. 创建文档
    create_documentation()

    # 4. 创建辅助脚本
    create_helper_scripts()

    # 5. 提示手动更新
    update_main_py()

    print(f"\n✅ 目录重组完成!")
    print(f"📚 查看新结构说明: data/config/README.md")
    print(f"🛠️ 使用管理工具: python data/config/run_manager.py")

if __name__ == "__main__":
    main()