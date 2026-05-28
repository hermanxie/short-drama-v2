# 101_动作

本目录用于探索新的动作提示词生成策略。

它是 `短剧_V2` 主项目下的独立实验区：

- 可以读取并借鉴上一级主项目经验。
- 不直接修改上一级主项目的规则、pipeline、输入和输出。
- 新策略、新模板、新流程和实验输出都保存在本目录内。

## 当前结构

```text
00_strategy_notes/  策略讨论、版本方案、取舍记录
01_rules/           本实验区专用规则
02_input/           实验输入材料
03_templates/       新提示词模板
04_pipeline/        实验脚本或半自动流程
05_output/          实验输出
06_review/          人工审核、测试反馈、对比结论
```

## 初始目标

先形成一套动作提示词新策略，再根据测试结果决定是否沉淀为可复用流程。

## 已部署 v1 文件

```text
01_rules/action_first_rules_v1.md
03_templates/action_first_prompt_template_v1.md
04_pipeline/action_first_workflow_v1.md
06_review/action_prompt_review_checklist_v1.md
00_strategy_notes/策略探索_v0.md
```

## 推荐使用顺序

1. 把本集脚本和图片说明放入 `02_input/EPXX/`。
2. 按 `04_pipeline/action_first_workflow_v1.md` 走完整流程。
3. 用 `03_templates/action_first_prompt_template_v1.md` 生成分镜提示词。
4. 用 `06_review/action_prompt_review_checklist_v1.md` 审核动作是否成立。
5. 输出结果放入 `05_output/EPXX/`。
