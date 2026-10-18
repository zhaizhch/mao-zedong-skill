# 暂存：GitHub Actions 工作流

`validate.yml` 是仓库自检工作流。它没有直接放在 `.github/workflows/`，是因为创建仓库时使用的
Personal Access Token 缺少 `workflow` 权限，GitHub 会拒绝推送工作流文件。

## 启用方式（二选一）

**A. 给 token 加 `workflow` 权限后推送**

```bash
mkdir -p .github/workflows
git mv ci/validate.yml .github/workflows/validate.yml
git commit -m "ci: 启用自检工作流"
git push
```

**B. 直接在网页上添加**

打开 `https://github.com/<owner>/<repo>/new/main/.github/workflows`，把 `ci/validate.yml`
的内容粘贴进去，提交即可。

启用后每次 push / PR 会自动跑：

- `python3 scripts/build_index.py --check`（生成物是否与语料同步）
- `python3 scripts/validate.py`（结构、契约、示例标注）
- 四个命令的冒烟测试
