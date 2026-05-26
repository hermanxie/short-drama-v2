# Cherry Pipeline V2

这个流水线把你原来的两个 Cherry 智能体串起来：

1. 先把完整剧本拆成统一的 `shot_block_plan.json`。
2. 草图提示词和视频提示词都只读取同一份 `shot_block_plan.json`。
3. 这样视频提示词不会重新理解剧情，而是严格继承分镜草图的每一格动作、机位、人物位置和台词分配。

## 文件来源

默认读取你已经验证过的 Cherry 系统提示词：

- `C:\Users\zhanchi\Desktop\cherry_agent\生成多宫格分镜草图的系统提示词.md`
- `C:\Users\zhanchi\Desktop\cherry_agent\生成视频的系统提示词.md`

## 推荐流程

### 1. 生成 Stage 1 规划请求

```powershell
python .\17_cherry_pipeline\cherry_pipeline.py plan-request --script .\17_cherry_pipeline\input\EP01_test_script.txt --episode EP17 --duration 150
```

输出：

```text
17_cherry_pipeline/requests/stage1_shot_block_plan_request.md
```

如果你没有配置 `OPENAI_API_KEY`，就把这个请求复制到大模型，让它只返回 JSON。

### 2. 保存模型返回的 JSON

把模型返回保存成：

```text
17_cherry_pipeline/output/EP17/model_shot_block_plan.json
```

然后验证并规范化：

```powershell
python .\17_cherry_pipeline\cherry_pipeline.py accept-plan --model-plan .\17_cherry_pipeline\output\EP17\model_shot_block_plan.json --episode EP17 --duration 150
```

输出：

```text
17_cherry_pipeline/output/EP17/shot_block_plan.json
```

### 3. 生成草图和视频提示词请求

```powershell
python .\17_cherry_pipeline\cherry_pipeline.py prompt-requests --plan .\17_cherry_pipeline\output\EP17\shot_block_plan.json --stage all
```

输出：

```text
17_cherry_pipeline/requests/stage2_storyboard_requests/block_01.md
17_cherry_pipeline/requests/stage3_seedance_requests/block_01.md
...
```

### 4. 本地直接渲染可审核提示词

不用 API 也可以先生成一版结构化提示词，用来审核分镜连续性：

```powershell
python .\17_cherry_pipeline\cherry_pipeline.py render-local --plan .\17_cherry_pipeline\output\EP17\shot_block_plan.json --stage all
```

输出：

```text
17_cherry_pipeline/output/EP17/block_01/storyboard_prompt.txt
17_cherry_pipeline/output/EP17/block_01/seedance_prompt.txt
```

## 关键原则

- `shot_block_plan.json` 是唯一中间蓝图。
- `storyboard_prompt.txt` 和 `seedance_prompt.txt` 永远来自同一个 block 和同一组 panel。
- 宫格数量由 `shot_block_plan.json` 的 `panel_count` 决定；规划阶段必须按动作密度混用 4/6/8/9/12，不能整集全部使用同一种宫格数。
- 台词只放在对应 panel，不会重复到所有镜头。
- 视频提示词会明确写出“对应分镜 1/2/3...”，方便你和草图宫格逐格核对。
