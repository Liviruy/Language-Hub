# Roadmap

> Language Hub 项目全流程指南

---

## 项目全景：整个系统怎么跑通

```
你收集单词 → CSV 文件
                  ↓
             language.db (数据仓库)
                  ↓
         ┌────────┼────────┐
         ↓        ↓        ↓
   查 Wiktionary  生成音频   导出 Anki
   (音标/释义)   (Edge TTS)  (.apkg 牌组)
         ↓        ↓
         ↓   上传 Cloudflare R2
         ↓        ↓
         └────────┼────────┘
                  ↓
             Astro 网站 (词典站)
                  ↓
         GitHub Actions 全自动
```

## 用通俗的方式理解

### Step 1：存原料 → language.db
你把在书里、剧里学到的单词写在 CSV 表格里，跑一个脚本把数据存进仓库——也就是 language.db 数据库。
就像把买来的面粉、糖、珍珠都放进仓库登记好。

### Step 2：查菜谱 → Wiktionary API
脚本自动去 Wiktionary（免费在线词典）查每个单词的音标、词性、释义、例句，存进数据库。
就像从网上找到奶茶配方，打印出来贴在原料旁边。

### Step 3：请人朗读 → Edge TTS
脚本扫描数据库里还没有音频的单词，用 Edge TTS 生成 mp3，上传到 Cloudflare R2。
已有音频的单词不会重复生成。

### Step 4：做学习卡片 → Anki 牌组
脚本自动生成 Anki 闪卡牌组，按语言和难度分类。导入 Anki App 就能刷。

### Step 5：建网站 → Astro 词典站
生成静态词典网站，可搜索单词、看音标释义、播放发音。

### Step 6：全自动流水线 → GitHub Actions
以上所有变成自动化流水线。你只需：加单词 → git push → 剩下的全自动。

---

## 阶段路线图

### Phase 1 — 项目初始化
目标：搭建项目的基础骨架（目录、Python 环境、配置文件）

### Phase 2 — 数据库设计
目标：创建 language.db，设计表结构
表：languages、words（JSON 字段存储含义/例句/音频/标签）

### Phase 3 — 导入器
目标：从 CSV / JSON 导入单词到数据库

### Phase 4 — 词典流水线
目标：自动查 Wiktionary，补充音标、释义、例句

### Phase 5 — 音频生成
目标：用 Edge TTS 生成发音，上传 R2

### Phase 6 — Anki 导出
目标：生成 .apkg 闪卡牌组

### Phase 7 — Cloudflare R2
目标：音频、文件上传云端，增量同步

### Phase 8 — 网站
目标：Astro 词典网站，搜索 + 详情页 + 暗色模式

### Phase 9 — API（可选）
目标：Cloudflare Workers REST API

### Phase 10 — 自动化
目标：GitHub Actions 全自动流水线
你 git push → 自动导入 → 查词典 → 生成音频 → 上传 R2 → 导出 Anki → 构建网站 → 部署

---

## 当前状态

- [x] 项目文档就绪
- [ ] Phase 1: 项目初始化
- [ ] Phase 2: 数据库设计
- [ ] Phase 3: 导入器
- [ ] Phase 4: 词典流水线
- [ ] Phase 5: 音频生成
- [ ] Phase 6: Anki 导出
- [ ] Phase 7: Cloudflare R2
- [ ] Phase 8: 网站
- [ ] Phase 9: API
- [ ] Phase 10: 自动化

---

## 你在每个阶段需要做什么

| 阶段 | 你做的事 |
|------|---------|
| Phase 1 | 确认目录结构没问题 |
| Phase 2 | 确认表结构满意 |
| Phase 3 | 准备 CSV 单词表 |
| Phase 4 | 确认查到的词典信息正确 |
| Phase 5 | 试听音频效果 |
| Phase 6 | 把 apkg 导入 Anki 试试 |
| Phase 7 | 配置 Cloudflare R2 账号 |
| Phase 8 | 打开网站看看效果 |
| Phase 9 | 决定是否需要 API |
| Phase 10 | 最终：只要加单词 + git push |
