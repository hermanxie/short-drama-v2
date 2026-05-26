from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "output" / "EP17" / "model_shot_block_plan.json"
TARGET = ROOT / "output" / "EP17_v2" / "model_shot_block_plan.json"


def shifted_time_ranges(duration: float, count: int) -> list[str]:
    ranges: list[str] = []
    for index in range(count):
        start = round(duration * index / count)
        end = round(duration * (index + 1) / count)
        if index == 0:
            start = 0
        if index == count - 1:
            end = round(duration)
        ranges.append(f"{start}s-{end}s")
    return ranges


def clone_panel(panel: dict, suffix: str, exact_action: str, camera_design: str, visual_goal: str) -> dict:
    clone = deepcopy(panel)
    clone["panel_id"] = suffix
    clone["exact_action"] = exact_action
    clone["camera_design"] = camera_design
    clone["dialogue"] = None
    clone["visual_goal"] = visual_goal
    return clone


def rebuild_block(block: dict, target_count: int, inserts: list[tuple[int, str, str, str]]) -> dict:
    panels = deepcopy(block["panel_plan"])
    for after_index, exact_action, camera_design, visual_goal in sorted(inserts, reverse=True):
        base = panels[after_index - 1]
        panels.insert(after_index, clone_panel(base, "", exact_action, camera_design, visual_goal))

    panels = panels[:target_count]
    ranges = shifted_time_ranges(float(block["duration"]), target_count)
    for index, panel in enumerate(panels, start=1):
        panel["panel_id"] = f"{block['block_id']}_P{index:02d}"
        panel["time_range"] = ranges[index - 1]

    block = deepcopy(block)
    block["panel_count"] = len(panels)
    block["panel_plan"] = panels
    return block


def main() -> None:
    plan = json.loads(SOURCE.read_text(encoding="utf-8"))
    plan["episode_id"] = "EP17_v2"

    specs = {
        "block_01": (
            6,
            [
                (1, "白光薄到几乎透明，楼兰王的手掌已经压出人形裂纹", "极近景 85mm，白光裂纹和怪手压迫构图", "把白光撑不住的危险视觉化"),
                (3, "亚特和解伊从破碎白光前掠过，楼兰王的爪影扫过他们身后的地面", "低角度广角 24mm，前景爪影快速掠过", "增强追杀距离只差一步的紧迫感"),
            ],
        ),
        "block_02": (
            8,
            [
                (1, "回廊尽头的阴影突然拉长，楼兰王的脚步声追近，二人速度被迫加快", "长焦 70mm 压缩回廊纵深，后景阴影推近", "让追兵距离在空间上变短"),
                (2, "解伊脚下一滑，亚特反手稳住她肩膀，没有停步继续拖拽", "近景 35mm 手持贴身跟拍，轻微晃动", "表现解伊体力和心理都濒临崩溃"),
                (3, "亚特用肩膀撞向木门前一瞬，眼神快速扫过门闩位置", "特写 50mm，从亚特眼神切到门闩", "让破门动作有明确判断过程"),
                (4, "楼兰王的影子压到门外回廊，亚特把解伊先推入屋内", "过肩 35mm，从门内看回廊黑影逼近", "把躲入小屋和追兵逼近压在同一画面"),
            ],
        ),
        "block_03": (
            6,
            [
                (1, "解伊跌坐到屋内地面，手掌撑住灰尘，惊魂未定地回望门口", "低角度近景 35mm，地面灰尘前景", "表现逃入屋内后的狼狈状态"),
                (3, "木桩卡入门后的凹槽，亚特用膝盖顶住下端防止滑脱", "特写 50mm，木桩与门槽咬合细节", "让封门动作更可信、更具体"),
            ],
        ),
        "block_04": (
            6,
            [
                (1, "解伊的眼泪滴到衣袖上，她听见门外余震后身体再次缩紧", "大特写 85mm，泪滴和颤抖手指", "把她的恐惧压到身体细节"),
                (3, "古铜镜从亚特怀里露出旧纹路，镜背符纹在光里一闪", "微距 100mm，铜镜符纹和手指细节", "强调铜镜不是普通道具"),
            ],
        ),
        "block_05": (
            8,
            [
                (1, "解伊手指碰到铜镜一瞬，镜面暗纹像呼吸一样微微亮起", "微距 100mm，指尖触镜和镜面暗纹", "把显魂触发点落在触碰瞬间"),
                (2, "铜镜反光沿着解伊袖口爬上肩线，像在寻找她背后的东西", "近景 50mm，反光移动路径构图", "让反光成为引导观众视线的线索"),
                (3, "亚特意识到镜面异动，抬手想阻止却已经来不及", "中近景 50mm，亚特手停在半空", "补足亚特的反应和失控感"),
                (4, "魔娅虚影的手指从解伊肩后浮现，几乎贴上她的脖颈", "特写 85mm，实体肩线与灵体手指叠合", "把灵体威胁推到身体距离"),
            ],
        ),
        "block_06": (
            6,
            [
                (2, "魔娅嘴角几乎看不见地上扬，黑雾在她唇边聚成细线", "极近特写 100mm，唇部和黑雾细节", "确认魂魄带有邪性意志"),
                (3, "解伊呼吸变急，魔娅的胸口轮廓却以相反节奏起伏", "中近景 50mm，双层轮廓呼吸错位", "表现二者既相连又不完全同步"),
            ],
        ),
        "block_07": (
            8,
            [
                (1, "镜中魔娅的红眼突然与解伊对视，解伊的瞳孔映出红点", "眼部大特写 100mm，瞳孔倒影构图", "强化目光撞上的惊吓点"),
                (2, "铜镜落地前翻转，短暂映出解伊和魔娅完全重叠的脸", "慢动作微距 60mm，铜镜翻转倒影", "让坠落前出现一帧关键真相"),
                (3, "解伊后退时肩膀撞上墙面，指尖抓出墙灰", "近景 50mm，墙面和手指前景", "把恐惧落实为身体碰撞"),
                (4, "亚特伸手想扶她却停住，意识到她已经看见不可挽回的东西", "中近景 35mm，亚特手停在前景", "为亚特后续坦白做心理过渡"),
            ],
        ),
        "block_08": (
            6,
            [
                (1, "铜镜中残留的黑雾像被亚特的手掌压回镜面边缘", "微距 85mm，手掌、镜缘和黑雾", "把铜镜重新收束为证据"),
                (3, "解伊听到魔娅两个字时，呼吸停住，眼神像被抽空", "大特写 85mm，解伊眼神和泪线", "突出身份反转落到她脸上的瞬间"),
            ],
        ),
        "block_09": (
            8,
            [
                (1, "亚特看向门外方向，确认魆屠和楼兰王背后的更大威胁", "侧脸特写 70mm，门缝光切过眼睛", "把敌人目的从追杀升级为献祭阴谋"),
                (2, "解伊听到取魂魄时，双手本能按住胸口，像护住自己的魂", "近景 50mm，手按胸口和颤抖肩线", "让台词中的取魂变成身体反应"),
                (3, "黑雾兵影在墙上短暂举起兵刃，随后被门缝光切碎", "中景 35mm，墙面军阵影子和光线对抗", "视觉化鬼蜮军团征讨中原"),
                (4, "亚特最后一个字落下，铜镜反光熄灭，屋内只剩解伊的喘息", "静态近景 50mm，铜镜暗下和空间压暗", "给解伊自责前留出沉默余韵"),
            ],
        ),
        "block_10": (
            9,
            [
                (1, "解伊的视线从亚特脸上滑落到地面铜镜，像在寻找否认的证据", "特写 85mm，视线下移到镜面", "让自我怀疑先从沉默开始"),
                (2, "她伸手想推开身后的虚影，却只抓到自己的发丝和空雾", "近景 50mm，手穿过黑雾", "表现她无法摆脱魔娅"),
                (3, "亚特向前半步想扶住她，却被黑雾和她的嘶吼逼停", "中景 35mm，亚特停步和黑雾阻隔", "让亚特无能为力"),
                (4, "魔娅虚影的脸贴近解伊耳侧，二者轮廓几乎合成一张脸", "大特写 85mm，双脸重叠构图", "把相融悬念推到最高"),
                (4, "解伊嘶吼结束后仍睁大眼睛，泪水持续下落，铜镜倒影停在双重人影", "定格式特写 100mm，泪脸与铜镜倒影交叉", "形成结尾钩子的最后一格"),
            ],
        ),
    }

    rebuilt = []
    for block in plan["shot_blocks"]:
        target_count, inserts = specs[block["block_id"]]
        rebuilt.append(rebuild_block(block, target_count, inserts))
    plan["shot_blocks"] = rebuilt

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(TARGET)


if __name__ == "__main__":
    main()
