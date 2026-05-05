# COMP3011 Coursework 2: Search Engine Tool — 完成规划清单

> 目标：冲击 **80–100分（Excellent to Outstanding）**
> 截止日期：**2026年5月12日**
> 提交内容：Minerva上提交一个PDF/TXT文件，包含视频链接、GitHub仓库URL、索引文件

## 当前完成状态（2026-05-03）

- 已完成代码实现：`crawler/indexer/search/main` 四个模块均已实现。
- 已完成正式索引：`data/index.json`，包含 **213 pages / 4654 terms**，使用默认 6 秒 politeness window 构建。
- 已完成测试：`33 passed`，`pytest-cov` 覆盖率 **97%**。
- 已完成文档：`README.md`、`docs/video_script.md`、`docs/genai_reflection.md`。
- 已完成 Git 提交：实现、测试、文档/索引已拆成有意义 commit。
- 已新增优化：exact phrase query、GitHub Actions CI、复杂度分析、benchmark 脚本。
- 仍需你完成：录制 5 分钟内视频、上传到可访问平台、确认 GitHub 仓库 public，并在 Minerva 提交视频链接/GitHub URL/索引文件。

---

## 一、项目结构（严格按照作业要求）

```
repository-name/
├── src/
│   ├── crawler.py       # 爬虫模块
│   ├── indexer.py       # 索引模块
│   └── search.py        # 搜索模块
│   └── main.py          # 主入口（命令行界面）
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── [index file]     # 编译好的索引文件
├── requirements.txt
└── README.md
```

---

## 二、功能实现清单

### 阶段1：爬虫（Crawler）— 目标网站：https://quotes.toscrape.com/

- [ ] 使用 `requests` 库发送 HTTP 请求
- [ ] 使用 `BeautifulSoup` 解析 HTML 页面
- [ ] 实现递归/BFS爬取所有页面（不遗漏任何子页面）
- [ ] **严格遵守 Politeness Window：每次请求之间至少等待 6 秒**
- [ ] 处理网络错误（超时、404、连接失败等），实现优雅的错误恢复
- [ ] 避免重复爬取同一URL（使用已访问URL集合）
- [ ] 记录爬取的所有页面URL

### 阶段2：索引构建（Indexer）

- [ ] 实现**倒排索引（Inverted Index）**，存储每个词在每个页面中的：
  - 出现频率（frequency）
  - 出现位置（positions）
  - 所在页面URL
- [ ] **大小写不敏感**：所有词统一转为小写
- [ ] 对词进行基本清洗（去除标点符号等）
- [ ] 选择合适的数据结构（推荐：`dict` 嵌套结构，或考虑 TF-IDF 权重）
- [ ] 为冲高分：实现 **TF-IDF 排名算法**（加分项）

### 阶段3：存储与加载（Storage & Retrieval）

- [ ] `build` 命令：爬取网站 → 构建索引 → 保存到文件系统（JSON 或 pickle 格式）
- [ ] `load` 命令：从文件系统加载已有索引
- [ ] 确保索引文件格式清晰可读（推荐 JSON）

### 阶段4：命令行界面（CLI）

实现以下四个命令：

- [ ] `> build` — 爬取、建索引、保存
- [ ] `> load` — 加载索引
- [ ] `> print <word>` — 打印某个词的倒排索引详情
- [ ] `> find <word1> [word2 ...]` — 查找包含所有指定词的页面列表
- [ ] 处理边界情况：
  - [ ] 查询不存在的词
  - [ ] 空查询
  - [ ] 多词查询（AND逻辑）
  - [ ] 特殊字符输入

---

## 三、测试清单（目标：>85% 覆盖率）

- [ ] `test_crawler.py`：
  - [ ] 测试正常页面爬取
  - [ ] 测试 Politeness Window 是否被遵守
  - [ ] 测试网络错误处理（mock requests）
  - [ ] 测试重复URL去重
- [ ] `test_indexer.py`：
  - [ ] 测试倒排索引正确性
  - [ ] 测试大小写不敏感
  - [ ] 测试词频统计
  - [ ] 测试位置记录
- [ ] `test_search.py`：
  - [ ] 测试单词查询
  - [ ] 测试多词查询
  - [ ] 测试不存在的词
  - [ ] 测试空查询
  - [ ] 测试 print 命令输出格式
- [ ] 使用 `pytest` + `pytest-cov` 生成覆盖率报告
- [ ] 考虑加入集成测试（integration tests）

---

## 四、代码质量要求（冲高分）

- [ ] 遵循 **PEP 8** 代码风格
- [ ] 每个函数/类有清晰的 **docstring**
- [ ] 使用 **type hints**（类型注解）
- [ ] 模块化设计，职责分离（crawler/indexer/search 各司其职）
- [ ] 实现防御性编程（defensive programming）
- [ ] 优化数据结构，考虑时间/空间复杂度

---

## 五、Git 版本控制要求（冲高分）

- [ ] 从项目开始就频繁提交，展示**增量开发过程**
- [ ] 每次提交有**有意义的 commit message**（如 `feat: add BFS crawler with politeness window`）
- [ ] 使用 **feature branches**（如 `feature/crawler`, `feature/indexer`, `feature/search`）
- [ ] 合并时使用 Pull Request（可选，但加分）
- [ ] 考虑使用 **semantic versioning** 打 tag（如 `v1.0.0`）
- [ ] 确保 GitHub 仓库为 **public**

---

## 六、README.md 要求（冲高分）

- [ ] 项目概述和目的
- [ ] 安装/环境配置说明
- [ ] 所有四个命令的使用示例
- [ ] 测试运行说明（`pytest --cov`）
- [ ] 依赖列表及安装方式（`pip install -r requirements.txt`）
- [ ] 架构概述（模块说明）
- [ ] 设计决策说明（数据结构选择理由）
- [ ] 参考资料

---

## 七、视频演示规划（严格5分钟内）

| 时间段 | 内容 | 时长 |
|--------|------|------|
| 0:00–2:00 | **Live Demo**：运行 build/load/print/find，展示多词查询和边界情况 | 2分钟 |
| 2:00–3:30 | **代码讲解 & 设计决策**：数据结构选择、爬虫/索引/搜索核心代码、权衡取舍 | 1.5分钟 |
| 3:30–4:00 | **测试演示**：运行测试套件，展示覆盖率报告，解释测试策略 | 0.5分钟 |
| 4:00–4:30 | **版本控制**：展示 Git commit 历史，解释开发工作流 | 0.5分钟 |
| 4:30–5:00 | **GenAI 批判性评估**：具体例子说明AI如何帮助/阻碍，对学习的影响 | 0.5分钟 |

### 视频技术要求
- [ ] 时长：**严格不超过5分钟**（超时扣分）
- [ ] 格式：MP4 或 MOV
- [ ] 分辨率：**最低 720p**
- [ ] 托管平台：YouTube（设为 unlisted）/ Google Drive / OneDrive
- [ ] 确保链接在无痕浏览器中可访问
- [ ] 清晰的音频旁白
- [ ] 代码/终端文字清晰可读（适当放大）

---

## 八、GenAI 批判性评估要点（占15%，重点！）

在视频中必须涵盖：

- [ ] 声明使用了哪些 AI 工具及用途
- [ ] **具体例子**：AI 在哪里帮助了你（如理解 BeautifulSoup API）
- [ ] **具体例子**：AI 在哪里出错或误导了你（如建议了错误的数据结构）
- [ ] 分析 AI 生成代码的质量和正确性
- [ ] 反思使用/不使用 AI 对学习的影响
- [ ] 讨论调试 AI 生成代码的挑战
- [ ] 评估对开发流程和时间管理的影响

> 注意：非声明或误导性声明 AI 使用构成学术不端行为

---

## 九、提交清单

- [ ] 在 Minerva 提交一个 PDF/TXT 文件，包含：
  - [ ] 视频演示链接（确认无痕浏览器可访问）
  - [ ] GitHub 仓库 URL（确认为 public）
  - [ ] 索引文件（作为附件上传，或提供下载链接）
- [ ] 截止日期：**2026年5月12日**

---

## 十、加分项（冲80+分）

- [ ] 实现 **TF-IDF 排名**，让 find 命令按相关性排序结果
- [x] 实现**高级查询处理**（如短语查询、通配符）
- [x] 实现**查询建议**（query suggestions）
- [x] 算法复杂度分析和性能基准测试（benchmarking）
- [x] 自动化测试流水线（GitHub Actions CI）
- [ ] 专业级 README（媲美开源项目）

---

## 评分权重参考

| 评分项 | 权重 |
|--------|------|
| 爬虫实现 | 10% |
| 索引实现 | 10% |
| 存储与加载（build/load） | 8% |
| 搜索功能（print/find） | 12% |
| 测试与覆盖率 | 20% |
| 代码质量与文档 | 10% |
| 版本控制与Git实践 | 5% |
| 视频演示质量 | 10% |
| GenAI 批判性评估 | 15% |
| **总计** | **100%** |
