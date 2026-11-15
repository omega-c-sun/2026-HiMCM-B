# Git：整理后建议推送的内容（只给命令）

在仓库根目录 `D:\Conditioner` 执行。先确认远程与分支名（下面用 `main` / `origin` 举例）。

## 1. 初始化（若还不是 git 仓库）

```text
cd /d D:\Conditioner
git init
git branch -M main
```

## 2. 看状态与忽略是否生效

```text
git status
git check-ignore -v papers/_v7_extract.txt model_v8/__pycache__ paper/scripts/polish_prose_deepseek.py
```

## 3. 暂存建议纳入版本的路径

```text
git add .gitignore README.md docs/
git add model_v8/*.py model_v8/README.md
git add data/sites_design_hour.csv data/fetch_open_meteo.py data/sites_open_meteo_check.csv data/diurnal/
git add paper/main.typ paper/template.typ paper/refs.yml paper/README.md paper/compile_v8.py
git add paper/sections/ paper/figures/ paper/scripts/polish_prose_deepseek.py paper/scripts/regen_figures.py
git add paper/18388_v9.pdf
git add model/ docs/model_*.md 2>nul
git add upload/ -- ':!upload/**/__pycache__' ':!upload/out/*.csv' ':!upload/out/*.png'
git add outputs_v8/*.csv
git status
```

不要加入：`.env`、含真实 API key 的备份、`papers/_v7_extract.txt`、`__pycache__`、参考用大 PDF（已在 `.gitignore`）。

## 4. 提交

```text
git commit -m "v9: fluids CEI delivery model, v7 fixes, Typst paper 18388_v9"
```

## 5. 关联远程并推送

```text
git remote add origin <你的仓库URL>
git push -u origin main
```

若远程已存在且只需更新：

```text
git push origin main
```

## 6. 可选：之后改完再推

```text
git add -u
git status
git commit -m "describe the change"
git push
```
