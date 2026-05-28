from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PIPELINE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = PIPELINE_DIR / "output"
DEFAULT_REQUESTS_DIR = PIPELINE_DIR / "requests"
DEFAULT_STORYBOARD_SYSTEM = Path(r"C:\Users\zhanchi\Desktop\cherry_agent\生成多宫格分镜草图的系统提示词.md")
DEFAULT_SEEDANCE_SYSTEM = Path(r"C:\Users\zhanchi\Desktop\cherry_agent\生成视频的系统提示词.md")

REQUIRED_BLOCK_FIELDS = {
    "block_id",
    "duration",
    "source_script_text",
    "scene_location",
    "characters",
    "dialogue_lines",
    "panel_count",
    "panel_plan",
}
REQUIRED_PANEL_FIELDS = {
    "panel_id",
    "time_range",
    "exact_action",
    "camera_design",
    "character_position",
    "environment_motion",
    "dialogue",
    "visual_goal",
}
FORBIDDEN_FINAL_TERMS = ("visual_focus", "camera_intention", "emotional_energy")
SEEDANCE_MAX_CHARS = 1970
SEEDANCE_TARGET_MIN_CHARS = 1900


class CherryPipelineError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.exists():
        raise CherryPipelineError(f"File is missing: {path}")
    if not path.is_file():
        raise CherryPipelineError(f"Expected a file, got directory: {path}")
    return path.read_text(encoding="utf-8-sig").strip()


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return path


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def load_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CherryPipelineError(f"Invalid JSON in {path}: {exc}") from exc


def normalize_dialogue(value: Any) -> dict[str, str] | None:
    if value in (None, "", {}, []):
        return None
    if not isinstance(value, dict):
        raise CherryPipelineError("dialogue must be an object or null.")
    required = ("speaker", "text", "emotion", "mouth_face")
    missing = [field for field in required if not clean_text(value.get(field))]
    if missing:
        raise CherryPipelineError("dialogue missing fields: " + ", ".join(missing))
    return {field: clean_text(value[field]) for field in required}


def normalize_dialogue_lines(value: Any) -> list[dict[str, str]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CherryPipelineError("dialogue_lines must be a list.")
    result: list[dict[str, str]] = []
    for item in value:
        dialogue = normalize_dialogue(item)
        if dialogue:
            result.append(dialogue)
    return result


def normalize_panel(panel: Any, block_id: str, index: int) -> dict[str, Any]:
    if not isinstance(panel, dict):
        raise CherryPipelineError(f"{block_id} panel {index} must be an object.")
    missing = sorted(REQUIRED_PANEL_FIELDS - set(panel))
    if missing:
        raise CherryPipelineError(f"{block_id} panel {index} missing fields: {', '.join(missing)}")
    normalized = {
        "panel_id": clean_text(panel["panel_id"]) or f"{block_id}_P{index:02d}",
        "time_range": clean_text(panel["time_range"]),
        "exact_action": clean_text(panel["exact_action"]),
        "camera_design": clean_text(panel["camera_design"]),
        "character_position": clean_text(panel["character_position"]),
        "environment_motion": clean_text(panel["environment_motion"]),
        "dialogue": normalize_dialogue(panel.get("dialogue")),
        "visual_goal": clean_text(panel["visual_goal"]),
    }
    empty = [key for key, value in normalized.items() if key != "dialogue" and not value]
    if empty:
        raise CherryPipelineError(f"{block_id} panel {index} has empty fields: {', '.join(empty)}")
    if not normalized["panel_id"].startswith(block_id):
        normalized["panel_id"] = f"{block_id}_P{index:02d}"
    return normalized


def normalize_block(block: Any, index: int) -> dict[str, Any]:
    if not isinstance(block, dict):
        raise CherryPipelineError(f"Block {index} must be an object.")
    missing = sorted(REQUIRED_BLOCK_FIELDS - set(block))
    if missing:
        raise CherryPipelineError(f"Block {index} missing fields: {', '.join(missing)}")
    block_id = clean_text(block["block_id"]) or f"block_{index:02d}"
    duration = float(block["duration"])
    if duration <= 0 or duration > 18:
        raise CherryPipelineError(f"{block_id} duration must be > 0 and <= 18 seconds.")
    characters = block["characters"]
    if not isinstance(characters, list) or not characters:
        raise CherryPipelineError(f"{block_id} characters must be a non-empty list.")
    panels = [normalize_panel(panel, block_id, i) for i, panel in enumerate(block["panel_plan"], start=1)]
    panel_count = int(block["panel_count"])
    if panel_count != len(panels):
        raise CherryPipelineError(f"{block_id} panel_count={panel_count}, actual panels={len(panels)}.")
    dialogue_lines = normalize_dialogue_lines(block["dialogue_lines"])
    panel_dialogue_texts = {panel["dialogue"]["text"] for panel in panels if panel["dialogue"]}
    for dialogue in dialogue_lines:
        if dialogue["text"] not in panel_dialogue_texts:
            raise CherryPipelineError(f"{block_id} dialogue not assigned to any panel: {dialogue['text']}")
    return {
        "block_id": block_id,
        "duration": round(duration, 2),
        "source_script_text": clean_text(block["source_script_text"]),
        "scene_location": clean_text(block["scene_location"]),
        "characters": [clean_text(item) for item in characters],
        "dialogue_lines": dialogue_lines,
        "panel_count": panel_count,
        "panel_plan": panels,
    }


def validate_plan(plan: Any, episode_id: str | None = None, duration_seconds: int | None = None) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise CherryPipelineError("shot_block_plan must be a JSON object.")
    blocks_raw = plan.get("shot_blocks")
    if not isinstance(blocks_raw, list) or not blocks_raw:
        raise CherryPipelineError("shot_block_plan must contain a non-empty shot_blocks list.")
    if not 8 <= len(blocks_raw) <= 16:
        raise CherryPipelineError(f"shot_blocks should contain 8-16 blocks, got {len(blocks_raw)}.")
    blocks = [normalize_block(block, index) for index, block in enumerate(blocks_raw, start=1)]
    panel_counts = [block["panel_count"] for block in blocks]
    if len(blocks) >= 4 and len(set(panel_counts)) == 1:
        raise CherryPipelineError(
            "All shot blocks use the same panel_count. The plan must vary 4/6/8/9/12 panels by action density."
        )
    return {
        "episode_id": clean_text(plan.get("episode_id")) or episode_id or "EP",
        "duration_seconds": int(plan.get("duration_seconds") or duration_seconds or round(sum(b["duration"] for b in blocks))),
        "plan_type": "cherry_pipeline_v2_shot_block_plan",
        "shot_blocks": blocks,
    }


def format_manifest_for_prompt(manifest: dict[str, Any] | None) -> str:
    if not manifest:
        return "未提供 assets_manifest.json。请在 shot_block_plan 中使用通用参考图锚定描述。"

    lines = [
        f"episode_id: {clean_text(manifest.get('episode_id'))}",
        f"aspect_ratio: {clean_text(manifest.get('aspect_ratio')) or '9:16'}",
    ]
    for section, title in (("characters", "人物参考"), ("scenes", "场景参考"), ("props", "道具参考")):
        values = manifest.get(section) or {}
        if not isinstance(values, dict) or not values:
            lines.append(f"{title}: 未登记")
            continue
        lines.append(f"{title}:")
        for name, item in values.items():
            if not isinstance(item, dict):
                continue
            refs = ", ".join(str(ref) for ref in item.get("refs", []))
            tag = clean_text(item.get("image_tag"))
            description = clean_text(item.get("description"))
            lines.append(f"- {name}: {tag}; refs={refs}; description={description}")
    return "\n".join(lines)


def build_plan_request(
    script: str,
    episode_id: str,
    duration_seconds: int,
    manifest: dict[str, Any] | None = None,
) -> str:
    manifest_text = format_manifest_for_prompt(manifest)
    return f"""你是 Cherry Pipeline V2 的总导演分镜规划器。

任务：阅读完整剧本，输出唯一中间蓝图 shot_block_plan.json。后续“多宫格分镜草图提示词”和“Seedance 视频提示词”都会严格读取这同一份 JSON，所以你必须把每个镜头动作、机位、人物位置、台词归属和环境动态写清楚。

硬性规则：
- 只能输出 JSON，不要 Markdown，不要解释。
- 将整集拆成 8-16 个 shot_blocks，每个 block 建议 8-15 秒，最长不超过 18 秒。
- 每个 block 对应一次可生成的多宫格草图和一条视频提示词。
- panel_count 可为 4、6、8、9、12，必须匹配动作复杂度，禁止整集全部使用同一个 panel_count。
- 4 帧只用于很简单、单一情绪或单一动作的短 block。
- 6 帧用于常规对话、走位、道具递接、情绪转折。
- 8 帧用于追逐、破门、灵异显现、身份揭露等需要动作递进的 block。
- 9 或 12 帧用于高潮段、崩溃钩子、强动作或多层视觉信息，需要逐格拆出起势、爆发、反应、余韵。
- 必须根据本集真实剧情密度自然混用 4/6/8/9/12，不允许机械套用单一宫格数。
- panel_plan 是核心。每个 panel 都要能被画成一格，并能被视频提示词逐格继承。
- 台词只放在真正发生口型的 panel.dialogue 内，不要复制到无台词镜头。
- exact_action 必须是可见动作，不要写“情绪升级”“继续推进”这类空话。
- 涉及动作、冲突、奔袭、转身、递接、攻击、躲避、追逐、法术/能量释放的 block，panel_plan 第一格必须直接从动作开始，不要以平静站姿、准备镜头、慢介绍或单纯建立环境开始。
- camera_design 必须包含景别、视角、焦段感和运动方式。
- character_position 必须交代左右、前中后景、面对/背对/过肩关系。
- environment_motion 必须交代本集真实存在的光、尘、风、沙、热浪、衣料、头发、道具、动物等会动的元素。
- visual_goal 写观众在这一格必须看懂的叙事信息。
- 必须使用下面 assets_manifest 中的人物、场景、道具说明作为视觉锚点。
- characters 字段只能写本 block 实际出场的角色/坐骑/重要灵体，不要把全局素材全塞进去。
- scene_location 应匹配 assets_manifest 中最接近的场景；道具出现时必须在 exact_action 或 environment_motion 中明确写出它的状态。

【本集素材索引 assets_manifest】
{manifest_text}

JSON 结构：
{{
  "episode_id": "{episode_id}",
  "duration_seconds": {duration_seconds},
  "shot_blocks": [
    {{
      "block_id": "block_01",
      "duration": 12,
      "source_script_text": "本 block 对应的短剧本文字",
      "scene_location": "具体场景位置",
      "characters": ["人物A", "人物B"],
      "dialogue_lines": [
        {{
          "speaker": "人物A",
          "text": "台词原文",
          "emotion": "这句台词的真实情绪",
          "mouth_face": "口型和面部肌肉动作"
        }}
      ],
      "panel_count": 6,
      "panel_plan": [
        {{
          "panel_id": "block_01_P01",
          "time_range": "0s-2s",
          "exact_action": "本 panel 中可见的具体动作，不要写总结句",
          "camera_design": "景别、视角、焦段感和运动方式",
          "character_position": "人物在左/右、前景/中景/后景、面对/背对/过肩关系",
          "environment_motion": "本场景里会动的光、风、沙尘、衣料、头发、道具等",
          "dialogue": {{
            "speaker": "人物A",
            "text": "台词原文",
            "emotion": "这句台词的真实情绪",
            "mouth_face": "口型和面部肌肉动作"
          }},
          "visual_goal": "观众在这一格必须看懂的叙事信息"
        }}
      ]
    }}
  ]
}}

完整剧本：
{script}
"""


def load_system_prompts(storyboard_system: Path, seedance_system: Path) -> tuple[str, str]:
    return read_text(storyboard_system), read_text(seedance_system)


def block_json(block: dict[str, Any]) -> str:
    return json.dumps(block, ensure_ascii=False, indent=2)


def build_storyboard_request(block: dict[str, Any], storyboard_system: str) -> str:
    return f"""你正在执行 Cherry Pipeline V2 Stage 2。

任务：只基于下面这个 block JSON，生成最终 `storyboard_prompt.txt`。这份提示词将用于生成多宫格分镜草图。

硬性规则：
- 必须遵守下方 Cherry 多宫格草图系统提示词。
- 只能使用这个 block JSON，不要回看完整剧本，不要自行改剧情。
- 必须完整覆盖 panel_plan 的每一格，顺序不可改变。
- 每一帧的动作、机位、人物位置、环境运动、画面目标必须来自对应 panel。
- 有 dialogue 的 panel 只能表现口型、表情、情绪，不要出现文字气泡。
- 无 dialogue 的 panel 不要添加台词。
- 涉及动作的草图一律直接从动作开始。不要以平静站姿、准备镜头或缓慢介绍开始。
- 只输出最终提示词正文，不要解释。

【Cherry 多宫格草图系统提示词】
{storyboard_system}

【唯一输入 block JSON】
{block_json(block)}
"""


def build_seedance_request(block: dict[str, Any], seedance_system: str) -> str:
    return f"""你正在执行 Cherry Pipeline V2 Stage 3。

任务：只基于下面这个 block JSON，生成最终 `seedance_prompt.txt`。这份提示词将用于 Seedance 2.0 或类似视频平台。

硬性规则：
- 必须遵守下方 Cherry 生视频系统提示词。
- 只能使用这个 block JSON，不要回看完整剧本，不要自行改剧情。
- 时序段落必须严格继承 panel_plan 的 time_range，并标明“对应分镜 N”。
- 每段动作、机位、人物位置、环境运动必须来自对应 panel。
- 台词只允许出现在对应 panel/time_range 中，禁止重复到其他镜头。
- 输出中必须强调严格对照同一 block 的分镜草图，逐格继承宫格内容。
- 最终视频提示词必须控制在 2000 字以内，适配即梦平台输入上限；在不损失生成效果的前提下压缩表达，优先保留人物一致性、逐格动作、机位、光影、台词归属和反向约束。
- 【全局风格与美学】禁止出现“暗黑奇幻”。
- 光影必须像现场拍摄：强方向主光、脸部/手部清晰补光、轮廓光、真实阴影层次，绝对避免平光。
- 镜头焦点必须优先锁定人物脸部、眼神、嘴唇、手部和关键道具，不要让背景抢焦。
- 禁止引入 block JSON 中不存在的任何道具、场景或超自然元素。
- 分镜草图只作为动作、构图、人物位置、镜头运动的理解参考，严禁把草图本身的视觉元素带入视频。
- 视频画面中绝对禁止出现草图线稿、铅笔纹理、宫格边框、编号、镜头参数文字、底部图例、彩色箭头、虚线箭头、红蓝绿橙黄标注线、UI、字幕、水印或任何说明文字。
- 只输出最终提示词正文，不要解释。

【Cherry 生视频系统提示词】
{seedance_system}

【唯一输入 block JSON】
{block_json(block)}
"""


def grid_layout(count: int) -> str:
    if count == 4:
        return "2x2"
    if count == 6:
        return "2x3"
    if count == 8:
        return "2x4"
    if count == 9:
        return "3x3"
    if count == 12:
        return "3x4"
    return f"{count}格结构化网格"


def dialogue_note(dialogue: dict[str, str] | None) -> str:
    if not dialogue:
        return ""
    return f"人物保持{dialogue['emotion']}，口型对应“{dialogue['text']}”，但画面不出现字幕或气泡。"


def clip_text(value: Any, limit: int) -> str:
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip("，。；、 ") + "…"


def ensure_clean_prompt(text: str) -> str:
    lowered = text.lower()
    found = [term for term in FORBIDDEN_FINAL_TERMS if term.lower() in lowered]
    if found:
        raise CherryPipelineError("Final prompt contains internal terms: " + ", ".join(found))
    return text.rstrip() + "\n"


def render_local_storyboard(block: dict[str, Any]) -> str:
    count = block["panel_count"]
    panels = []
    for index, panel in enumerate(block["panel_plan"], start=1):
        panels.append(
            f"帧{index} ({panel['camera_design']})：画面左上角带有清晰的数字“{index}”。"
            f"{panel['exact_action']} {panel['character_position']} {dialogue_note(panel['dialogue'])}"
            f"红色粗实线箭头标示身体动势，蓝色虚线箭头标示镜头运动，绿色框线服务于{panel['visual_goal']}，"
            f"橙色短线标示主光方向，黄色碎线表现{panel['environment_motion']}。"
        )
    return ensure_clean_prompt(f"""{count}帧原始预演动作分镜拼贴画，专为竖屏9:16短剧画幅设计，呈现早期动作编舞预可视化质感。

【全局风格与环境绝对还原法则】
实际故事板绘图必须仅为黑白：粗糙的铅笔线条、最小细节、快速手势绘图能量、简单的解剖结构构建以及强烈的轮廓可读性。保持艺术作品轻量、动态且未完成，就像早期打斗编舞预可视化一样。
环境参考锚定：地点为{block['scene_location']}。保持用户提供场景参考图的核心地貌/建筑结构、空间比例、光影基调、空气介质、战火/风沙/烟尘层次和本 block 实际出现的道具。大量负空间，禁止画面拥挤，禁止引入本集未登记元素。
动作起手规则：涉及动作、冲突、奔袭、转身、递接、攻击、躲避、追逐、法术/能量释放的草图，一律直接从动作开始。不要以平静站姿、准备镜头或缓慢介绍开始。

【全局主体与一致性设定】
出场人物：{", ".join(block['characters'])}。人物严格参考用户上传的人物图，保持面部、发型、服装、饰物、道具和身体比例完全一致。
无论在哪个帧中，都绝对保持人物轮廓比例、服装褶皱走向、道具尺度、原始铅笔质感，以及与写实环境的融合，绝不允许结构突变。

【分镜画面序列】
{chr(10).join(panels)}

【标注系统与底部图例】
箭头逻辑：红色实线=身体动势，蓝色虚线=相机轨迹，绿色框线=构图引导，橙色短线=光线方向，黄色碎线=元素 VFX。所有标注沿负空间延伸，不遮挡主体面部。
底部图例：画面最下方预留干净横向条带，标注："RED = BODY MOVEMENT | BLUE = CAMERA MOVEMENT | GREEN = FRAMING / COMPOSITION | ORANGE = LIGHTING DIRECTION | YELLOW = ELEMENTAL VFX / ENERGY"。

【布局与反向约束】
布局：{count}帧排列成{grid_layout(count)}的干净、结构化拼贴网格，细边框分隔。仅左上角有数字序号，顶部含镜头参数，底部含图例。无对话框、无 UI、无水印、无多余文字、无色彩污染。
--ar 9:16 --style raw --s 100 --no panel bleeding, overlapping text, blurry arrows, smooth rendering, cartoon, extra limbs, deformed hands, chaotic background, color spill, static poses
""")


def seedance_timeline(block: dict[str, Any], field_limit: int) -> list[str]:
    timeline = []
    for index, panel in enumerate(block["panel_plan"], start=1):
        dialogue = panel["dialogue"]
        line = (
            f"[{panel['time_range']}]对应分镜{index}:"
            f"【{clip_text(panel['camera_design'], field_limit)}】"
            f"{clip_text(panel['character_position'], field_limit + 18)}；"
            f"{clip_text(panel['exact_action'], field_limit + 28)}；"
            f"环境:{clip_text(panel['environment_motion'], field_limit + 12)}；"
            f"目的:{clip_text(panel['visual_goal'], field_limit)}。"
        )
        if dialogue:
            line += (
                f"台词:{dialogue['speaker']}“{clip_text(dialogue['text'], 46)}”"
                f"({clip_text(dialogue['emotion'], 28)}，{clip_text(dialogue['mouth_face'], 34)})。"
            )
        timeline.append(line)
    return timeline


def build_seedance_prompt_detailed(block: dict[str, Any], field_limit: int) -> str:
    timeline = "\n".join(seedance_timeline(block, field_limit))
    return f"""【风格】
真人写实短剧电影质感，8K照片级写实，秦汉西域历史战争实拍感，低饱和胶片色。强方向主光来自火光/月光/战场反光/斜侧逆光，人物脸部和手部必须有清晰柔和补光、眼神光、鼻梁颧骨唇部手背高光，保留脸颊明暗交界；用轮廓光把人物从烟尘、城楼、军阵、骨船背景中剥离。镜头始终优先对焦脸、眼、嘴、手和关键道具，背景只给战场纵深、风沙、火光和压迫感，拒绝平光、灰雾、欠曝、五官糊、背景抢焦。

【主体与分镜参考】
地点:{block['scene_location']}。出场:{", ".join(block['characters'])}。严格参考上传图，保持面部、发型、服装材质、颜色、饰物、道具、身形比例一致，群体数量和空间比例稳定。严格对照同一block多宫格分镜草图，逐格继承动作、机位、人物位置、环境动态和台词归属；草图只作动作/构图/运镜参考，最终画面必须是真人写实电影，不得把草图本身画进视频。

【时序分镜】
{timeline}

【声音】
纯Foley+对应台词，绝对无BGM。只保留本段真实存在的风沙、马蹄、脚步、兵器、盔甲、衣料、骨链、法杖能量、火焰、喘息等现场声；台词只在对应镜头出现，禁止跨镜头重复。

【物理与禁忌】
布料、头发、烟尘、火光、沙粒、马匹、兵器、法杖能量、鬼蜮船阴影、军阵推进都要符合真实重力和空间关系，脸手不能被烟尘或过曝火光遮没。禁止新增未登记人物/场景/道具/超自然元素；禁止草图线稿、宫格边框、编号、镜头参数、底部图例、彩色箭头、虚线、辅助线、UI、水印、字幕、说明文字；禁止塑料感、肢体错误、脸手失焦、过度磨皮、运镜卡顿、物理崩坏。
"""


SEEDANCE_DETAIL_PADDING = (
    "补充:保持每个镜头的前中后景关系清楚，人物视线和手部动作必须连续；"
    "烟尘、衣摆、发丝、火把、盔甲反光随动作变化，不能静止贴图；"
    "台词镜头要看见嘴唇和面部肌肉，非台词镜头只给呼吸、眼神和肢体反应；"
    "战场群体只作纵深和压迫，不抢主要人物焦点；"
    "所有镜头与上一格自然衔接，动作方向、光源方向和空间位置不能跳变。"
)


def pad_seedance_prompt(prompt: str) -> str:
    prompt = prompt.rstrip()
    if len(prompt) >= SEEDANCE_TARGET_MIN_CHARS:
        return prompt + "\n"
    remaining = SEEDANCE_MAX_CHARS - len(prompt) - 1
    if remaining <= 0:
        return prompt + "\n"
    addition = ""
    while len(addition) < remaining and len(prompt) + len(addition) + 1 < SEEDANCE_TARGET_MIN_CHARS:
        addition += SEEDANCE_DETAIL_PADDING
    if len(addition) > remaining:
        addition = addition[:remaining].rstrip("，。；、 ") + "。"
    return f"{prompt}\n{addition}\n"


def render_local_seedance(block: dict[str, Any]) -> str:
    best_under_limit = ""
    for field_limit in (120, 105, 92, 80, 68, 58, 48, 40, 32):
        prompt = ensure_clean_prompt(build_seedance_prompt_detailed(block, field_limit))
        if len(prompt) <= SEEDANCE_MAX_CHARS:
            if not best_under_limit or len(prompt) > len(best_under_limit):
                best_under_limit = prompt
            if len(prompt) >= SEEDANCE_TARGET_MIN_CHARS:
                return prompt
    if best_under_limit:
        return ensure_clean_prompt(pad_seedance_prompt(best_under_limit))
    raise CherryPipelineError(f"{block['block_id']} seedance prompt still exceeds {SEEDANCE_MAX_CHARS} chars.")


def command_plan_request(args: argparse.Namespace) -> list[Path]:
    script = read_text(args.script)
    manifest = load_json(args.manifest) if args.manifest else None
    request = build_plan_request(script, args.episode, args.duration, manifest)
    return [write_text(DEFAULT_REQUESTS_DIR / "stage1_shot_block_plan_request.md", request)]


def command_accept_plan(args: argparse.Namespace) -> list[Path]:
    plan = validate_plan(load_json(args.model_plan), episode_id=args.episode, duration_seconds=args.duration)
    return [write_json(args.output / plan["episode_id"] / "shot_block_plan.json", plan)]


def command_prompt_requests(args: argparse.Namespace) -> list[Path]:
    plan = validate_plan(load_json(args.plan))
    storyboard_system, seedance_system = load_system_prompts(args.storyboard_system, args.seedance_system)
    written: list[Path] = []
    if args.stage in ("storyboard", "all"):
        for block in plan["shot_blocks"]:
            written.append(write_text(DEFAULT_REQUESTS_DIR / "stage2_storyboard_requests" / f"{block['block_id']}.md", build_storyboard_request(block, storyboard_system)))
    if args.stage in ("seedance", "all"):
        for block in plan["shot_blocks"]:
            written.append(write_text(DEFAULT_REQUESTS_DIR / "stage3_seedance_requests" / f"{block['block_id']}.md", build_seedance_request(block, seedance_system)))
    return written


def command_render_local(args: argparse.Namespace) -> list[Path]:
    plan = validate_plan(load_json(args.plan))
    episode_dir = args.output / plan["episode_id"]
    written: list[Path] = [write_json(episode_dir / "shot_block_plan.json", plan)]
    for block in plan["shot_blocks"]:
        block_dir = episode_dir / block["block_id"]
        if args.stage in ("storyboard", "all"):
            written.append(write_text(block_dir / "storyboard_prompt.txt", render_local_storyboard(block)))
        if args.stage in ("seedance", "all"):
            written.append(write_text(block_dir / "seedance_prompt.txt", render_local_seedance(block)))
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cherry Pipeline V2: align storyboard-grid and video prompts through one shot plan.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan-request", help="Create Stage 1 request for shot_block_plan.json.")
    p.add_argument("--script", required=True, type=Path)
    p.add_argument("--episode", required=True)
    p.add_argument("--duration", required=True, type=int)
    p.add_argument("--manifest", type=Path, help="Optional assets_manifest.json for visual anchors.")
    p.set_defaults(func=command_plan_request)

    p = sub.add_parser("accept-plan", help="Validate and normalize model_shot_block_plan.json.")
    p.add_argument("--model-plan", required=True, type=Path)
    p.add_argument("--episode", required=True)
    p.add_argument("--duration", required=True, type=int)
    p.add_argument("--output", default=DEFAULT_OUTPUT_DIR, type=Path)
    p.set_defaults(func=command_accept_plan)

    p = sub.add_parser("prompt-requests", help="Create Stage 2/3 model requests from confirmed shot_block_plan.json.")
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--stage", choices=["storyboard", "seedance", "all"], default="all")
    p.add_argument("--storyboard-system", default=DEFAULT_STORYBOARD_SYSTEM, type=Path)
    p.add_argument("--seedance-system", default=DEFAULT_SEEDANCE_SYSTEM, type=Path)
    p.set_defaults(func=command_prompt_requests)

    p = sub.add_parser("render-local", help="Render deterministic review prompts from shot_block_plan.json without API.")
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--stage", choices=["storyboard", "seedance", "all"], default="all")
    p.add_argument("--output", default=DEFAULT_OUTPUT_DIR, type=Path)
    p.set_defaults(func=command_render_local)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    written = args.func(args)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
