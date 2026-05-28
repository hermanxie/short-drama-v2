# AGENTS Changelog

## 2026-05-26

- 新增项目级 `AGENTS.md`。
- 新增项目说明文件 `README.md`。
- 补充标准结构目录。
- 明确 `短剧_V2` 项目需谨慎维护，不随意移动或覆盖已有核心文件。

## 2026-05-28

- 校准 `AGENTS.md` 中的核心流程路径：当前实际核心流程位于 `05_pipeline/`，不再写作 `17_cherry_pipeline/`。
- 更新执行前检查范围：分别检查 `05_pipeline/` 代码，以及 `02_input/`、`03_assets/`、`06_output/` 的输入、素材和输出变更。
- 更新核心脚本与编译验证命令为 `05_pipeline/cherry_pipeline.py`。
