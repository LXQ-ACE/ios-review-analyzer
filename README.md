
# iOS App Review 评论分析与版本规划工具

基于用户评论的全链路 AI 产品分析工具，覆盖评论抓取、数据清洗、语义分析、PRD生成、测试用例产出完整闭环。

## ✨ 核心功能

### 1. 多源数据获取
- 支持苹果官方 iTunes RSS 接口在线抓取美国区评论
- 支持本地 CSV / JSON 文件导入
- 内置字段自动映射，兼容不同格式的数据源

### 2. 四层数据清洗
- 空内容、短内容自动过滤
- 重复评论去重
- 相似度去重（基于 TF-IDF + 余弦相似度）
- 字段标准化与格式统一

### 3. AI 智能语义分析
- 动态主题分类，无硬编码分类
- 核心痛点与核心好评自动识别
- 矛盾反馈检测
- 证据等级与情感倾向标注
- 全链路评论 ID 可追溯

### 4. 智能 PRD 生成
- 自动输出产品背景与问题分析
- 分版本迭代需求规划
- 需求优先级分级（P0/P1/P2/P3）
- 用户价值与对应问题点关联

### 5. 测试用例自动生成
- 基于需求自动产出功能测试用例
- 包含前置条件、执行步骤、预期结果
- 用例级别分级（高/中/低）

### 6. 结果一键导出
- 评论数据 CSV 导出
- AI 语义分析报告 Markdown 导出
- 产品需求文档 PRD 导出
- 全链路完整分析报告导出

## 🛠️ 技术栈

- **前端**：Streamlit
- **后端**：Python 3.10+
- **大模型**：DeepSeek API（OpenAI 兼容格式）
- **数据校验**：Pydantic v2
- **数据处理**：Pandas
- **缓存机制**：本地文件缓存

## 📦 项目结构

```

ios-review-analyzer/
├── config/
│   └── settings.py          # 全局配置（主题、模型、常量）
├── core/
│   ├── schemas.py           # Pydantic 数据结构定义
│   ├── llm_client.py        # 大模型客户端封装
│   ├── analyzer.py          # AI 分析核心业务逻辑
│   ├── data_fetcher.py      # 评论数据抓取
│   └── data_cleaner.py      # 数据清洗
├── utils/
│   ├── cache.py             # 缓存工具
│   └── exporter.py          # 导出工具
├── data/
│   └── sample_reviews.csv   # 内置示例数据集
├── .env.example             # 环境变量示例
├── .gitignore
├── app.py                   # 主程序入口
├── requirements.txt
└── README.md

```

## 🚀 快速开始

### 1. 安装依赖
```
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录新建 `.env` 文件：

```
DEEPSEEK_API_KEY=你的API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
LLM_TEMPERATURE=0.3
ENABLE_CACHE=True
```

### 3. 启动项目

```
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501` 即可使用。

## 📝 使用说明

1. **选择数据源**：在线抓取 / 本地文件导入 / 内置示例数据
2. **配置 AI 功能**：勾选需要启用的分析能力
3. **点击「开始全流程分析」**
4. **查看结果**：数据概览、语义分析、PRD 规划、测试用例
5. **导出报告**：一键导出所需格式文件

## ⚠️ 注意事项

- 在线抓取受网络环境限制，若无法获取数据，请使用本地文件导入或内置示例数据
- 大模型调用会产生费用，建议开启缓存降低成本
- 所有数据仅在本地处理，不会上传至第三方服务器