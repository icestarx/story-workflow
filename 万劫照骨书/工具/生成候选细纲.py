#!/usr/bin/env python3
"""Generate 250 non-locked, contract-complete Chinese-named outline candidates.

This is a planning utility, not a prose generator. It keeps the full-book
coverage auditable; each chapter must still be rebased and locked before draft.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "scripts"))

from project_paths import chapter_filename
VERSION = "1.0.0"
STEPS = ["起因", "试探", "受阻", "反转", "交接"]

VOLUMES = [
    ("残簿照骨", "雁回泽", [
        ("死人领灯", "查清死者阿七为何在霜降夜领名", "命灯异动与外账禁令", "陆沉舟发现死籍倒潮时辰", "第四盏灯敲门", "mystery.yanhui, power.zhaogu_book"),
        ("盐砂官印", "取得死籍的合法查验资格", "巡籍司认定陆沉舟伪造证据", "顾青梧从疫方看出盐砂", "裴照夜奉令到来", "foreshadow.salt_seal, char.gu_qingwu"),
        ("外账追索", "找到仍活着的雁回泽证人", "巫仰以邪修罪名封泽", "祝离交出三盏旧灯", "证人被带走", "char.zhu_li, faction.heaven_archive"),
        ("倒潮证词", "把笔迹、灯油与潮汐串成证据", "裴照夜坚持程序不能越过", "陆以照骨书看见官印债纹", "劫务车队抵达", "char.pei_zhaoye, mystery.yanhui"),
        ("灯铺余烬", "保住证据并说服裴照夜同行", "巫仰焚毁灯铺嫁祸外账者", "裴为幸存者违令拔剑", "外吏令的条件", "char.pei_zhaoye, foreshadow.salt_seal"),
        ("无名口供", "让被除名者的证词进入公堂", "证人没有合法姓名", "顾青梧以医案证明身份连续", "劫务库要求封口", "char.gu_qingwu, world.outer_ledger"),
        ("账页缺角", "找到雁回泽被征调的书面链条", "账页被拆成数段流向不同人", "陆失去父亲笑声换来残响", "缺角指向海路", "power.zhaogu_book, char.lu_chenshou"),
        ("公堂反照", "在巡籍司公堂击破疫潮说", "巫仰以合法劫务令反压", "三方证据证明令牌被秘密改档", "巫仰说出上级代号", "mystery.yanhui, faction.tianheng_court"),
        ("祭地潮图", "追问雁回泽案是否孤例", "道庭只肯给临时名权", "巫仰承认五处祭地", "逆潮海图浮现", "foreshadow.tide_reverse, world.mingxu"),
        ("外吏令", "用胜利换取行动资格而非安全", "书天监将陆列为可追索外吏", "陆接令出海查第二处", "海市收名的传闻", "char.lu_chenshou, mystery.haishi"),
    ]),
    ("海市问名", "无渡海", [
        ("逆潮入海", "借潮图抵达只开一夜的海市", "观潮楼拒载无名者", "宁妄以妹妹姓名交换合作", "船票要押上真名", "foreshadow.tide_reverse, char.ning_wang"),
        ("名字作价", "摸清海市的姓名定价规则", "每次询价都会被市场记住", "宁妄识破一份假契", "顾青梧被人叫错名字", "mystery.haishi, faction.hundred_trades"),
        ("潮眼暗线", "找到被抵押者的去处", "骆春山受楼规限制不能泄图", "陆用旧潮印换她一次指路", "海市开始闭市", "char.luo_chunshan, faction.tidewatch_tower"),
        ("忘亲之人", "验证姓名被夺后的真实后果", "被忘者被亲人当成骗子", "旧歌与灯油留下不可抹的行为痕迹", "宁妄见到妹妹", "mystery.haishi, power.zhaogu_book"),
        ("赎名之价", "阻止宁妄用更多人名换回妹妹", "契约允许他合法付款", "宁妄发现妹妹的名字已被拆卖", "他把赎契藏起", "char.ning_wang, relation.lu_ning"),
        ("观潮楼账", "逼观潮楼承认中立获利", "海图属于全楼而非骆春山个人", "骆公开一段被篡的潮线", "楼主派人追船", "char.luo_chunshan, faction.tidewatch_tower"),
        ("市井反契", "让被抵押者看到并理解自己的契", "海市用幻市隔开买卖双方", "陆立下短期责任簿共享残响", "所有人的债同时压来", "power.five_realms, mystery.haishi"),
        ("撕契之夜", "在妹妹面前让宁妄主动拒绝赎名", "宁妄终于拿到完整赎契", "他撕契并留下补偿账", "海市券开始崩裂", "char.ning_wang, faction.hundred_trades"),
        ("沉市潮声", "让海市交易链无法转移到别处", "书天监切断回岸潮路", "骆以真实海图带众人逆潮", "五祭地连线显影", "foreshadow.tide_reverse, faction.heaven_archive"),
        ("空壳请柬", "承接道庭对海市案的反扑", "获救者尚未完全恢复亲缘", "三宗会盟传来突破空壳", "无字契随请柬到来", "mystery.zongmen, foreshadow.blank_contract"),
    ]),
    ("诸宗欠命", "三宗会盟", [
        ("空壳道场", "确认三名突破者为何只剩命火", "宗门互相扣帽子", "越观尘接案并封锁现场", "第一张无字契出现", "mystery.zongmen, char.yue_guanche"),
        ("装订孔", "把三宗残卷接出共同来源", "证据都在宗门密库", "祁听雪发现相同装订孔", "密库名册被删", "char.qi_tingxue, faction.heaven_archive"),
        ("立簿试案", "以新境界分摊调查风险", "陆必须公开自己的记忆损失", "团队自愿立簿成功", "有人从账簿里撤约", "power.five_realms, char.lu_chenshou"),
        ("错认帮凶", "查清一名受害者为何替书天监送信", "照骨残响只给债向不给动机", "陆错判并伤害同伴信任", "真正受益者逃走", "power.zhaogu_book, relation.lu_gu"),
        ("师门旧页", "迫使顾青梧面对悬灯寺旧账", "账页会牵连救过她的人", "顾交出旧页并失去师门信任", "药灯库被封", "char.gu_qingwu, faction.suspended_lamp"),
        ("审籍法庭", "让越观尘看见程序被匿名债掏空", "所有人都可拿紧急劫务免责", "无字契反噬一名高阶修士", "越要求公开审契", "char.yue_guanche, mystery.zongmen"),
        ("剑院裂缝", "让裴照夜在剑院与外账者间选择", "功勋派用矿脉威胁剑院", "裴公开拔剑条款", "祁听雪与家族决裂", "char.pei_zhaoye, char.qi_tingxue"),
        ("诸宗欠账", "把匿名挪债的完整链条公布", "书天监烧毁账本并制造混乱", "陆用多人见证保住副本", "闻玄策留下无名箴言", "mystery.zongmen, faction.heaven_archive"),
        ("第四劫影", "确认封印压力已超出旧制度承受", "公开真相引发各州拒役", "逆潮海图与无字契互证", "闻玄策传来邀约", "world.mingxu, foreshadow.blank_contract"),
        ("失踪掌簿", "让幕后人从影子进入角色关系", "闻玄策以救灾者身份获拥护", "队伍知道顾青梧旧师就是他", "第四劫提前一月", "char.wen_xuance, relation.gu_wen"),
    ]),
    ("无名渡劫", "五处祭地", [
        ("提前的劫", "在五处祭地先兆中救下一座村庄", "旧封印要求立即征名", "闻玄策提出无名方案", "第一批人主动失名", "mystery.wujie, char.wen_xuance"),
        ("无名会分裂", "听见无名者不同的真实选择", "激进派认为陆仍在维护天籍", "温和派要求退出与补偿", "祝离的名册被抢", "faction.nameless_society, char.zhu_li"),
        ("旧师之门", "查明顾青梧为何被保留下来", "闻玄策以师徒情谊要求她继承锚位", "顾拒绝被指定为祭材", "她的命灯开始失控", "char.gu_qingwu, char.wen_xuance"),
        ("一城失名", "验证无名方案是否真的无痛", "闻玄策先抹去一城名字", "亲缘、证词与防线同时瓦解", "越观尘承认旧法也有罪", "mystery.wujie, char.yue_guanche"),
        ("拒绝签字", "让陆拒绝以一城人名换北陆安稳", "盟友认为他害死人", "陆放弃最快的封印补丁", "队伍分裂撤约", "arc.hero, faction.tianheng_court"),
        ("公开受审", "使越观尘和裴照夜各自承担旧制度责任", "审判会被书天监利用成内斗", "二人公开受审并交权", "公众第一次提出反对席位", "char.yue_guanche, char.pei_zhaoye"),
        ("共契初灯", "证明知情自愿的见证能稳定一处裂口", "参与者都有撤约理由", "祁听雪公开阵图并成功守住一夜", "锚数不足被量化", "char.qi_tingxue, power.five_realms"),
        ("潮脉回响", "把五祭地连成可行动路线", "冥墟回响吞噬陆的记忆锚", "骆春山交出所有中立海图", "陆忘记父亲的脸", "char.luo_chunshan, foreshadow.tide_reverse"),
        ("无名代价", "让众人理解完全失名的终局后果", "激进派仍愿赌一次", "闻玄策开始忘记顾青梧的名字", "他抢走照骨书母本", "foreshadow.no_name_price, char.wen_xuance"),
        ("最后的锚", "确认主角必须付出的终局条件", "共契少一枚不可替代的自知锚", "陆发现自己的名字可补缺口", "所有人进入五卷倒计时", "world.mingxu, char.lu_chenshou"),
    ]),
    ("万劫同书", "冥墟", [
        ("无字试验", "验证匿名债为何让封印失稳", "各派只信对己有利的解释", "无字契在公开试验中反噬", "五类反对者名单出现", "foreshadow.blank_contract, mystery.wujie"),
        ("各自归名", "让每名同伴争取不同的共契条件", "旧仇与现实补偿阻碍结盟", "宁妄拿出退出补偿账", "第一批商盟签名", "char.ning_wang, faction.hundred_trades"),
        ("五地同裂", "在祭地同时开裂前布置共契节点", "书天监抢先篡改名册", "盐砂与灯油被重释为定位证据", "祝离灯火熄灭", "foreshadow.salt_seal, char.zhu_li"),
        ("纸灰乳名", "揭开自知姓名才是封印锚的条件", "陆已忘却太多雁回泽旧事", "纸灰乳名让他想起众人曾自报姓名", "他决定成为无名见证人", "foreshadow.ash_name, power.zhaogu_book"),
        ("众名公审", "让闻玄策在所有受害者前接受审问", "他以五劫压迫众人快速签字", "顾青梧叫出他遗忘的旧名", "闻承认无名方案的代价", "char.wen_xuance, char.gu_qingwu"),
        ("撤约之权", "把反对与退出写进共契而非排除异议", "有人临阵撤约引发封印晃动", "越观尘按公开程序补上补偿", "共契仍差主锚", "char.yue_guanche, relation.lu_yue"),
        ("破阙前夜", "让陆与同伴告别而不替他做决定", "照骨书要求以可记名权换破阙", "每人明确同意或拒绝的边界", "冥墟裂口开启", "char.lu_chenshou, power.five_realms"),
        ("万劫同书", "在五劫中执行众名共契", "闻玄策与旧天籍同时争夺锚点", "陆以无名见证改写征调规则", "所有早期债纹回响", "mystery.wujie, foreshadow.no_name_price"),
        ("不入天籍", "处理胜利后的责任与审判", "众人想为陆重新登记姓名", "陆拒绝任何例外特权，闻受审", "雁回泽正式立碑", "char.wen_xuance, world.tianji"),
        ("新灯领名", "回扣首章并留下平静余波", "无名的陆无法被制度记录", "一盏新命灯由幸存者共同点起", "人们叫出他的名字", "char.lu_chenshou, char.zhu_li"),
    ]),
]

def make_outline(chapter, volume_no, volume_name, place, block, local_step):
    phase, goal, obstacle, result, hook, canon = block
    refs = ", ".join(f"[[{item.strip()}]]" for item in canon.split(","))
    title = f"{phase}·{STEPS[local_step]}"
    next_title = f"第 {chapter + 1} 章" if chapter < 250 else "全书尾声"
    return f"""# 第 {chapter} 章：{title}

## 章节信息

- 卷：第 {volume_no} 卷《{volume_name}》；章节功能：{phase}的{STEPS[local_step]}节点。
- 状态：候选
- Canon 版本：{VERSION}
- 承接：第 {chapter - 1} 章的未决压力（首章为开篇快照）。
- 交付：{result}。

## 入章状态

地点：{place}；人物以陆沉舟与当前卷已入场角色为限。陆持照骨书，任何照见都要支付记忆代价；角色只知道此前章节已证明的信息。

## 核心事件与因果

触发：{phase}出现新的异常或期限。行动：众人试图{goal}。阻力：{obstacle}。结果：{result}。新局面：{hook}，迫使{next_title}接住。

## 场景节拍

1. 用可见异常开启，明确本章期限。
2. 陆沉舟提出目标并从现有证据/资源行动。
3. 对手按自身制度利益施压，而非无故阻挠。
4. 同伴以各自知识边界给出支持、反对或条件。
5. 选择造成可追溯结果：{result}。
6. 由结果导出下一章问题：{hook}。

## 情绪曲线

从警觉（4/10）进入受压与选择（7/10），以结果后的短暂释放或更深不安（6/10）收束；不得以纯说明替代情绪变化。

## 章首钩子

{phase}的异常先于解释出现：{hook}。

## 爽点与代价

爽点：主角或同伴凭已铺垫的证据、契约、专业能力推进{goal}。代价：照骨书、命灯、契票、信任或程序中的至少一项受损；胜利不得免除下一层责任。

## 伏笔操作

- 引用：{refs}。
- 操作：本章推进一个既有线索；若新设细节，只能标为候选 delta，不得当作 Canon。

## 角色状态变化

陆沉舟在资源、记忆、关系或知识上发生可记录变化；至少一名同伴以自身目标作出不能被主角代替的选择。

## 章尾钩子

{hook}。下一章必须直接承担这一压力，而不是换题。

## 字数预算

目标 4,000 字；六个场景节拍合计 3,600–4,400 字。

## Canon 冲突检查

检查 [[world.tianji]]、[[world.outer_ledger]]、[[power.zhaogu_book]] 与 {refs}：候选细纲未新增世界规则；写正文前必须按最新 Canon 重基并锁定。
"""

def main():
    outlines = ROOT / "细纲"
    outlines.mkdir(exist_ok=True)
    index = ["# 章节索引", "", "| 章 | 卷 | 标题 | 章节功能 | 细纲状态 | 正文状态 | Canon 版本 | 备注 |", "|---:|---:|---|---|---|---|---|---|"]
    chapter = 1
    for volume_no, (volume_name, place, blocks) in enumerate(VOLUMES, 1):
        for block in blocks:
            for step in range(5):
                title = f"{block[0]}·{STEPS[step]}"
                path = outlines / chapter_filename(chapter)
                path.write_text(make_outline(chapter, volume_no, volume_name, place, block, step), encoding="utf-8")
                index.append(f"| {chapter} | {volume_no} | {title} | {block[0]} | 候选 | 未写 | {VERSION} | 写前重基 |")
                chapter += 1
    (ROOT / "规划" / "章节索引.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"generated {chapter - 1} candidate outlines")

if __name__ == "__main__":
    main()
