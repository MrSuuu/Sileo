# Sileo 源规范（debs / depictions / 索引）

⛔ **改封面图、效果截图、描述页之前，先读这一节。** 以下是 2026-10-08 实战定稿，照抄别自己发挥。

## 一、目录与生成器

```
debs/                              # 所有 .deb，每个包只保留最新一版
depictions/<stem>.json / .html     # 描述页，stem = 包名最后一个 "." 之后的部分
Packages / .bz2 / .gz              # 索引，由脚本生成，勿手改
update_packages.py                 # 索引生成器
```

改完 depiction 或 deb 都要自己跑 `python3 update_packages.py`（只有 debs/** 变更才触发 CI）。

## 二、⛔ 描述页 JSON 定稿结构（顺序即页面顺序）

```
DepictionSpacerView(spacing:16)   ← 封面卡【上方】留空
DepictionImageView                ← 封面卡
DepictionMarkdownView             ← 正文描述
DepictionSeparatorView
DepictionHeaderView("信息")
DepictionTableTextView × N
DepictionHeaderView("效果预览")   ← 截图区标题
DepictionScreenshotsView          ← 效果截图（页面最底部）
```

### 封面卡：字段名大写 `URL`，尺寸填显示磅值

```json
{"class":"DepictionImageView",
 "URL":"https://MrSuuu.github.io/Sileo/depictions/liquidass27-cover-v4.jpg",
 "width":390,"height":207,"cornerRadius":12,"alignment":1,"xPadding":0}
```

- ⛔ **必须是大写 `URL`**：写小写 `url` ⇒ 控件静默不渲染 ⇒ **封面永远空白**（踩过一整晚）。
- ⛔ `width`/`height` 填**显示磅值**（约 390 = 屏宽），**不是原图像素**。
- ⛔ **不要用顶层 `headerImage`**：它渲染成页面最顶部的通栏横幅（图标上方），泽哥明确否掉。

### 效果截图：每张只给 `url`

```json
{"class":"DepictionScreenshotsView","itemCornerRadius":6,"itemSize":"{150, 346}",
 "screenshots":[{"accessibilityText":"Screenshot",
                "url":"https://MrSuuu.github.io/Sileo/depictions/liquidass27-shot1-v4.jpg"}]}
```

- ⛔ 不要加 `fullSizeURL`。
- `itemSize` 用 `"{150, 346}"` 小缩略图尺寸，照参考源加 `accessibilityText`。

## 三、⛔ 改内容必须换 URL（缓存）

**Sileo 按 URL 缓存 depiction 和图片，按「包名+版本」决定要不要重拉。** 包版本号不变时，
即使内容改了、源刷新了、用户清了缓存，设备也可能永远用旧版。「刷新源」只刷 Packages 索引，不清 depiction 缓存。

- 改 depiction/json → `update_packages.py` 里 `depiction_rev = {'liquidass27': 'N'}` **+1**。
- 改图片内容 → **换文件名**（`-v4.jpg` → `-v5.jpg`）。⛔ 图片缓存 key 按路径算、**忽略 `?v=` 查询参数**，
  只加查询参数换不掉缓存，会一直复用最早那张拉失败的空图。
- 当前 `liquidass27` 修订号 = **9**。
- 参考实现：`https://jimkanuo.github.io/apt-repo/depiction/com.ngkhoi.26home.json`

## 四、图片体积

`sips` 压缩（⛔ 别用 `-h` 当缩放参数，`-h` 是设高度）：

```bash
# 截图
sips -s format jpeg -s formatOptions 65 --resampleWidth 640  shotN.jpg --out shotN.jpg
# 封面
sips -s format jpeg -s formatOptions 70 --resampleWidth 1000 cover.jpg --out cover.jpg
```

压缩后同步 JSON 里 `DepictionImageView` 的 `width`/`height`（若原来写的是原图像素）。

## 五、上线核验（Pages 有部署延迟 + CDN 缓存）

```bash
# 等约 20–60s 后轮询，加 ?v=<ts> 穿透 CDN 缓存
curl -s "https://MrSuuu.github.io/Sileo/depictions/liquidass27.json?v=9" | python3 -m json.tool | head -20
curl -s "https://MrSuuu.github.io/Sileo/Packages?v=$(date +%s)" | grep -c "json?v=9"
```

push 被 CI 机器人「🤖 自动更新索引」拦住 ⇒ `git pull --rebase origin main`，冲突只在
`Packages*` 三个文件，以自己这份为准，`GIT_EDITOR=true git rebase --continue`。