# 泽哥源 — 个人越狱插件源

个人使用的 Cydia / Sileo 越狱源，适配 iOS 越狱环境（roothide / Relaxin / CydiaSubstrate）。

## 添加源

在 Sileo / Zebra / Cydia 中添加源地址：

```
https://MrSuuu.github.io/Sileo
```

## 包含插件

| 插件 | 标识 | 版本 | 说明 |
|---|---|---|---|
| 悬浮底栏 | com.zegeyoudaoli.floatingtabbar | 1.0 | 给部分自带 App 的底栏加悬浮半透效果 |
| Liquid Glass Popup | com.zegeyoudaoli.liquidalass | 1.0.0 | 为 iOS 17+ 弹窗添加 iOS 26 液态玻璃效果 |
| RealCPU 两行显示 | com.zegeyoudaoli.realcputwoline | 1.0 | 控制中心实时 CPU 频率+占用率两行显示 |
| Culprit 汉化 | com.zegeyoudaoli.culpritzh | 1.0-6 | Culprit 崩溃查看器界面汉化 |

## 目录结构

```
├── Packages / Packages.bz2   # 源索引（自动生成）
├── debs/                     # 插件安装包
├── depictions/               # 插件详情页
├── sileo.json                # Sileo 源描述
├── update_packages.py        # 索引生成脚本
└── .github/workflows/        # 自动更新工作流
```

## 添加新插件

1. 把新的 `.deb` 放进 `debs/` 目录
2. 本地跑 `python3 update_packages.py`（或直接 push，Actions 会自动跑）
3. `git add . && git commit -m "Add xxx" && git push`

GitHub Actions 会自动重新生成 `Packages` 索引，Sileo 刷新即可看到新包。

## 开启 GitHub Pages

`Settings → Pages → Source: Deploy from a branch → Branch: main → / (root)`

之后源地址即为 `https://MrSuuu.github.io/Sileo`。
