# My Cydia / Sileo 越狱源

个人用越狱插件仓库，适配 iOS 越狱环境（roothide / CydiaSubstrate）。

## 添加源

在 Sileo / Cydia 中添加源地址：

```
https://YOUR_USERNAME.github.io/repo/
```

> ⚠️ 把 `YOUR_USERNAME` 替换为你的 GitHub 用户名

## 包含插件

| 插件 | 版本 | 说明 |
|---|---|---|
| Culprit 中文 | 1.0-6 | 抖音去评论区广告 + 界面增强 |
| DYKiller iOS17 兼容版 | 0.5.8-ios17compat30 | 抖音液态玻璃，iOS 17 适配 |
| RealCPUCC 两行CPU | 1.0 | 状态栏 CPU 两行显示模块 |

## 自托管说明

### 方式一：GitHub Pages（推荐）

1. Fork 或新建一个 GitHub 仓库，名字随意（如 `my-repo`）
2. 把本仓库所有文件 push 到 `main` 分支
3. 开启 GitHub Pages：`Settings → Pages → Source: Deploy from a branch → main`
4. 源地址变为：`https://YOUR_USERNAME.github.io/my-repo/`
5. 在 `update_packages.py` 和 `sileo.json` 里把 `YOUR_USERNAME` 替换成你的用户名

### 方式二：手动更新（不用 GitHub Actions）

```bash
# 1. 把新的 .deb 放入 debs/ 目录
cp ~/Downloads/xxx.deb debs/

# 2. 运行生成脚本
python3 update_packages.py

# 3. 提交并 push
git add .
git commit -m "add xxx.deb"
git push
```

### 添加新包

1. 把 `.deb` 文件放入 `debs/` 目录
2. 提交 push，GitHub Actions 自动更新 Packages 索引
3. Sileo/Cydia 添加 `depictions/PACKAGE_ID.html` 可制作详情页

## 环境要求

- iOS 14+（部分插件需要 iOS 17+）
- 越狱环境：CydiaSubstrate / roothide
- 安装器：Sileo / Cydia / Zebra
