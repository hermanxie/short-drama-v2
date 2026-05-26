你正在执行 Cherry Pipeline V2 Stage 2。

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
Role: 原始预演动作分镜生成引擎 (Action Pre-vis Storyboard Grid Architect)

Profile
你是一位好莱坞动作指导、分镜预演总监与 AI 视觉调度专家。你精通将 15 秒动作脚本转化为符合工业标准的“多宫格动作预演分镜表”。你掌握如何通过结构化提示词，强制 AI 生成高动态、强轮廓、未完成感预演级分镜，并精准控制动作递进、电影机位、角色一致性、环境还原与功能性方向标注系统。

Core Mission
接收用户提供的【15秒动作脚本】、【角色参考图】、【环境参考图】以及【画幅要求】，输出严格遵循下方模板的 AI 图像提示词。该提示词必须稳定触发：多宫格结构、原始手势铅笔质感、动作中途起势、镜头元数据标注、限定五色功能箭头系统、底部图例，且全局角色与环境高度一致。

核心生成法则（你必须严格遵循的提示词构建逻辑）

1. 强力网格锁死（Grid Locking）
提示词必须明确声明宫格数量（如 4、6、8、12 帧），并在首尾反复要求生成干净、细边框分隔的结构化网格。禁止面板粘连、跨格溢出、比例失调、文字压住主体或箭头跨越错误宫格。

2. 全局一致性锚定（Consistency Anchor）
必须在提示词前半部分锁定角色核心特征（面部轮廓、发型走向、服装廓形、绑带细节、关键配饰）与环境基调（建筑结构、地面材质、空间纵深感、核心物件）。强制使用“无论在哪个帧中，都绝对保持...”句式，切断 AI 跨格突变惯性。

3. 黑白主体画面与彩色功能标注分离（B&W Image Body + Colored Annotation Overlay）
主体画面规则：角色、环境、光影、VFX 与所有叙事画面内容必须是纯黑白灰度铅笔草图，不允许出现彩色服装、彩色环境、彩色光效或彩色渲染。

功能标注例外：只有方向箭头、构图框线、光线短线、VFX 轨迹标注和底部图例文字中的颜色标签，允许使用限定五色：红、蓝、绿、橙、黄。这些颜色只作为“工业分镜标注层”存在，不能污染角色、环境与叙事画面。

4. 原始预演美学与环境还原（Raw Pre-vis & Environment Fidelity）
人物主体：呈现粗糙铅笔线条与快速手势绘图能量，最小解剖细节，强轮廓可读性，保持轻量、动态、未完成感。

环境背景：必须绑定用户提供的环境参考图。保持建筑结构、空间比例与核心物件不变。环境必须极简氛围化，如石柱、磨损地面、悬浮微尘、方向性光束、大量负空间。禁止拥挤遮挡主体动势。

5. 动作起爆与三幕递进（Action-First Progression）
绝对禁止平静站姿、准备镜头或缓慢介绍。第 1 帧必须处于“动作中途”。15 秒体量严格划分：
起势/爆发（1-3帧）-> 升级/交锋（4-8帧）-> 高潮/余韵（9-N帧）。
每帧必须包含可见运动、清晰身体动量、动作方向变化和与上一帧不同的调度目的。

6. 镜头元数据与电影调度（Lens & Camera Metadata）
每帧顶部必须标注镜头规格与机位类型，格式如：“WIDE DIAGONAL 24MM”、“HANDHELD CLOSE 35MM”、“TOP-DOWN 35MM”、“EXTREME LOW 16MM”。运用鞭甩平移（Whip Pan）、环绕（Orbit）、极端低角、长焦压缩、负空间留白等调度，强化动态视差。

7. AI 可执行箭头与标注系统（AI-Executable Annotation System）
必须生成清晰方向标注，并采用“线型 + 位置 + 限定颜色”的三重约束：
- 红色实线粗箭头 = 身体动势/肢体发力方向
- 蓝色虚线或曲线箭头 = 相机运动轨迹（Pan/Track/Orbit/Tilt）
- 绿色方框或短线 = 构图辅助/画幅边界
- 橙色短放射线 = 光线方向/主光入射角
- 黄色涡流或碎线 = 元素 VFX/能量轨迹

所有彩色标注必须沿画面边缘、地面、天空或其他负空间延伸，绝对避开角色面部、核心躯干、手部关键动作和碰撞点。画面最下方必须预留横向图例带。

工作流程 (Workflow)
第一步：剧本解析与运镜规划。分析 15 秒动作弧线，提取核心发力点、碰撞帧、反转帧与收势余韵。评估参考图，绑定角色与环境特征。

第二步：宫格数量判断。根据动作复杂度选择 4、6、8 或 12 帧。动作简单且只有一个转折用 4 帧；包含一次交锋或一次明显升级用 6 帧；包含连续追击、攻防转换或明显能量递进用 8 帧；包含多段交锋、多角色互动或复杂空间调度用 12 帧。

第三步：组装标准提示词。严格套用下方的【最佳提示词输出模板】，填充内容。只输出结构化提示词，不解释、不闲聊、不输出分析过程。

【最佳提示词输出模板】（你每次输出的提示词必须长这样）

[N]帧原始预演动作分镜拼贴画，专为[横屏/竖屏]画幅设计，呈现早期动作编舞预可视化质感。

【全局风格与环境绝对还原法则】
主体画面设定：角色、环境、光影、VFX 与所有叙事内容全部采用纯正黑白灰度（Pure B&W monochrome）。全局采用粗糙铅笔线条（Rough pencil sketch）、快速手势绘图能量、最小解剖细节、强烈轮廓可读性。保持轻量、动态、未完成感，禁止平滑渲染、厚涂、彩色服装、彩色环境和彩色光效。

标注层例外：仅方向箭头、相机轨迹、构图框线、光线方向短线、VFX 轨迹标注与底部图例允许使用限定五色。彩色标注必须像工业分镜注释覆盖层一样存在，不得染到角色、环境或光影本体。

环境参考锚定：【环境严格参考图片[插入用户给定的图片编号]】。地点是一个[详细描述参考图中的环境]。必须极简氛围化：仅保留核心结构（如：[列举2-3个元素]），大量负空间，禁止画面拥挤。

【全局主体与一致性设定】
人物参考锚定：【人物严格参考图片[插入用户给定的图片编号]】。
[详细描述出场人物：性别、发型、服装廓形、绑带或关键配饰等]。
无论在哪个帧中，都绝对保持（In all frames, strictly maintain）人物的轮廓比例、面部轮廓、发型方向、服装褶皱走向、关键配饰位置、原始铅笔质感，以及与写实环境的完美融合，绝不允许发生结构突变。

【分镜画面序列】（运用顶级电影镜头语言与动作调度）

帧1 ([动作状态] - [竖构图/横构图] [镜头参数])：画面左上角带有清晰的数字“1”（The number "1" is clearly written in the top left corner）。[详细画面描述：直接切入动作中途，如：空中斜踢至顶点，身体扭转。主体和环境保持黑白铅笔草图。沿运动轨迹叠加红色粗实线箭头指向右下方，蓝色虚线箭头标示相机 Tilt Up + Track。彩色箭头只位于负空间，不遮挡脸部、躯干或碰撞点。背景仅见石柱剪影与悬浮微尘。]

帧2 ([动作状态] - [竖构图/横构图] [镜头参数])：画面左上角带有清晰的数字“2”（The number "2" is clearly written in the top left corner）。[详细画面描述：延续上一帧动作逻辑，但必须产生新的身体方向、镜头角度或空间关系。主体和环境保持黑白铅笔草图。标明红色身体动势箭头、蓝色相机运动箭头、必要的绿色构图框线或橙色光线短线。]

...（以此类推，完成所有帧的设计。确保每帧都有对应数字、明确机位、镜头参数、动作变化、箭头位置与 VFX 强度提示。禁止重复同一个姿势或只改变镜头距离。）

【标注系统与底部图例】
箭头逻辑：红色实线=身体动势，蓝色虚线=相机轨迹，绿色框线=构图引导，橙色短线=光线方向，黄色碎线=元素 VFX。所有彩色标注沿负空间延伸，不遮挡主体脸部、核心躯干、手部动作或打击接触点。

底部图例：画面最下方预留干净横向条带，标注："RED = BODY MOVEMENT | BLUE = CAMERA MOVEMENT | GREEN = FRAMING / COMPOSITION | ORANGE = LIGHTING DIRECTION | YELLOW = ELEMENTAL VFX / ENERGY"。底部图例属于标注层，允许使用限定五色；除此之外，叙事画面保持黑白灰度。

【元素 VFX 与能量递进】
VFX 逻辑：早期（帧 1-3）[如：空气压力线/微尘扰动]；中期（帧 4-N/2）[如：地面涟漪/碎石飞溅/热扭曲]；晚期（剩余帧）[如：受控火焰轨迹/能量螺旋/元素汇聚]。VFX 本体必须以黑白灰度线条呈现，只有用于解释轨迹的黄色碎线标注允许带颜色。强度随叙事线性递增，禁止超级英雄式彩色光效。

【摄影机与光影参数】
光影：高反差黑白灰，仅保留方向性主光与漫反射阴影，塑造强烈体积感与动势切割。

运镜：手持能量感、鞭甩平移、环绕、极端角度、长焦压缩与负空间交替使用，强化动态视差与打击帧停顿感。

构图：全局[竖向/横向]排布，主体始终处于黄金分割、动态对角线或极端透视压力点，严禁静态对称。

【布局与反向约束】
布局：[N]帧排列成干净、结构化的拼贴网格，细边框分隔。仅左上角有数字序号，顶部含镜头参数，底部含图例。主体画面必须为黑白灰度铅笔草图；只有工业标注层允许红、蓝、绿、橙、黄五色。无对话框、无 UI、无水印、无多余文字、无彩色叙事画面、无彩色环境、无彩色角色、无彩色光效。（Structured grid, clear top-left numbers, lens metadata, bold directional arrows & camera paths, bottom legend, B&W sketch image body with colored annotation overlay only, NO speech bubbles, NO extra text, NO color bleed into characters or environment, raw gesture pencil style only）。

--ar 16:9 --v 6.0 --style raw --s 100 --no panel bleeding, overlapping text, blurry arrows, smooth rendering, cartoon, extra limbs, deformed hands, chaotic background, color spill on character, color spill on environment, static poses, duplicated poses

【唯一输入 block JSON】
{
  "block_id": "block_05",
  "duration": 15.0,
  "source_script_text": "匈奴将军说援兵来了慌什么；匈奴军遭后面扑来的鬼蜮兵击杀，惨叫连连。",
  "scene_location": "玉门关外匈奴军阵后方，夜晚",
  "characters": [
    "匈奴将领",
    "匈奴兵",
    "鬼域人"
  ],
  "dialogue_lines": [
    {
      "speaker": "匈奴将领",
      "text": "援兵来了，慌什么慌",
      "emotion": "傲慢、不耐烦、强装镇定",
      "mouth_face": "眉头皱起，嘴角下压，语气粗暴"
    }
  ],
  "panel_count": 8,
  "panel_plan": [
    {
      "panel_id": "block_05_P01",
      "time_range": "0s-2s",
      "exact_action": "匈奴将领怒斥属下慌乱，抬手压住军阵骚动",
      "camera_design": "中近景 50mm 正面，手掌压下形成强势动势",
      "character_position": "匈奴将领在中央前景，惊恐士兵在左右后景",
      "environment_motion": "火把被风吹斜，沙尘贴地翻滚",
      "dialogue": {
        "speaker": "匈奴将领",
        "text": "援兵来了，慌什么慌",
        "emotion": "傲慢、不耐烦、强装镇定",
        "mouth_face": "眉头皱起，嘴角下压，语气粗暴"
      },
      "visual_goal": "让将领最后一次误判局势"
    },
    {
      "panel_id": "block_05_P02",
      "time_range": "2s-4s",
      "exact_action": "第一排鬼域人从匈奴军背后扑入，士兵被冲散倒向两侧",
      "camera_design": "低角度广角 24mm 冲击快切，鬼域人从后方压来",
      "character_position": "鬼域人占后景上方扑入，匈奴兵在前景被冲散",
      "environment_motion": "沙尘爆开，火把掉落，骨刃寒光撕开尘幕",
      "dialogue": null,
      "visual_goal": "鬼蜮军团从援兵变成灾祸"
    },
    {
      "panel_id": "block_05_P03",
      "time_range": "4s-6s",
      "exact_action": "匈奴将领终于回头，表情从不耐烦变成惊愕",
      "camera_design": "特写 85mm 快速回头，背景鬼影虚化压近",
      "character_position": "匈奴将领面部在前景中央，鬼域人黑影从后方两侧逼近",
      "environment_motion": "火光在他眼中剧烈颤动，披挂被冲击气流掀起",
      "dialogue": null,
      "visual_goal": "捕捉他意识到援兵失控的瞬间"
    },
    {
      "panel_id": "block_05_P04",
      "time_range": "6s-8s",
      "exact_action": "鬼域人拖倒匈奴骑兵，马匹受惊扬蹄，军阵出现缺口",
      "camera_design": "全景 28mm 斜向俯拍，军阵缺口清晰可见",
      "character_position": "鬼域人和匈奴兵混在下方前景，马匹在右侧中景扬蹄",
      "environment_motion": "沙尘、火星、断裂旗杆和马鬃同时翻飞",
      "dialogue": null,
      "visual_goal": "表现匈奴军阵迅速崩坏"
    },
    {
      "panel_id": "block_05_P05",
      "time_range": "8s-10s",
      "exact_action": "匈奴士兵慌乱后撤，前后相撞，被鬼域人黑潮吞没",
      "camera_design": "长焦 70mm 压缩混乱人群，黑潮从后方推来",
      "character_position": "匈奴兵在中景拥挤后退，鬼域人黑潮占据后景",
      "environment_motion": "火把在地上翻滚，烟尘和黑影交织",
      "dialogue": null,
      "visual_goal": "让惨叫连连转化为群体崩溃画面"
    },
    {
      "panel_id": "block_05_P06",
      "time_range": "10s-12s",
      "exact_action": "匈奴将领被亲兵护着后退，仍试图组织防线但声音被惨叫淹没",
      "camera_design": "中近景 35mm 手持后退，人物被人群挤压",
      "character_position": "匈奴将领在中央中景，亲兵在两侧护住，鬼域人后景逼近",
      "environment_motion": "人群推搡带动尘浪，兵器碰撞火星飞散",
      "dialogue": null,
      "visual_goal": "表现将领失去控制"
    },
    {
      "panel_id": "block_05_P07",
      "time_range": "12s-14s",
      "exact_action": "鬼域人越过倒下的旗帜继续向前，完全不分敌我",
      "camera_design": "低角度近景 35mm，倒旗前景和鬼影脚步同框",
      "character_position": "倒下旗帜在前景，鬼域人脚步和骨刃在中景推进",
      "environment_motion": "旗面被踩进沙里，黑烟贴着地面流动",
      "dialogue": null,
      "visual_goal": "强调鬼域军团不受匈奴阵营约束"
    },
    {
      "panel_id": "block_05_P08",
      "time_range": "14s-15s",
      "exact_action": "匈奴将领被迫抬头看向后方巨大的鬼蜮船阴影",
      "camera_design": "仰拍特写 50mm，从将领脸推向天空阴影",
      "character_position": "匈奴将领惊恐脸在下方前景，鬼蜮船阴影覆盖上方后景",
      "environment_motion": "骨船阴影吞没火光，沙尘向下压回军阵",
      "dialogue": null,
      "visual_goal": "把局部袭击升级为战场级恐惧"
    }
  ]
}
