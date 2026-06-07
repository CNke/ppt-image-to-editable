# PPT 图片转可编辑 PPT

[English](README.md) | 简体中文

这个仓库提供的是一个给 Codex 使用的 skill，用于把 PPT 页面图片转换为可编辑的 PowerPoint 文件。

它不是一个独立的 PPT 生成器。它不会直接根据文字提示设计整套 PPT，也不会自己凭空生成 PPT 页面。它的作用是辅助 Codex 将已经存在的 PPT 图片尽量原封不动地还原为可编辑的 `.pptx` 文件：文字尽量变成可编辑文本框，适合用原生形状复刻的部分用 PowerPoint 形状，复杂视觉元素则保留为完整的高清图片元素。

使用这个 skill 的前提是：你已经获得了 PPT 页面图片。推荐流程是先用 `gpt-image` 生成或取得高质量 PPT 图片，再用本 skill 将这些图片转换为可编辑的 PowerPoint 页面。

## 能做什么

- 指导 Codex 进行高保真的图片转 PPT 重建。
- 在批量转换前，强制先生成并确认一个样页。
- 尽可能把图片中的文字重建为可编辑 PowerPoint 文本框。
- 对复杂图标、产品图、图表、装饰组件等视觉元素，优先保持完整视觉效果。
- 在原生形状会明显降低还原度时，使用完整高清图片元素保真。
- 在交付前校验资产决策、版式计划、媒体引用和生成的 PPTX 文件完整性。

## 不能做什么

- 不能直接从文字提示生成完整 PPT。
- 不能替代 PPT 设计模型或图片生成模型。
- 不能在没有源 PPT 图片的情况下完成转换。
- 不能保证所有元素都变成 PowerPoint 原生可编辑形状；当保真和可编辑性冲突时，优先保证视觉还原。

## 推荐流程

1. 先生成或取得 PPT 页面图片。
   - 推荐：使用 `gpt-image` 先生成高质量 PPT 页面图片。
   - 也可以使用已有图片版/扁平化 PPT 导出的页面图片。
2. 将 `ppt-image-to-editable/` 安装或复制为 Codex skill。
3. 让 Codex 检查 PPT 图片或图片版 PPTX。
4. 先制作 1 页可编辑样页。
5. 审核样页并确认重建风格。
6. 样页通过后，为每一页建立资产决策计划。
7. 为每一页建立版式计划。
8. 批量转换整套 PPT，并校验生成的 `.pptx` 文件。

## 项目结构

```text
.
|-- README.md
|-- README.zh-CN.md
|-- requirements.txt
|-- examples/
|   |-- asset_decision_plan.example.json
|   `-- layout_plan.example.json
`-- ppt-image-to-editable/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- references/
    |   |-- conversion-playbook.md
    |   `-- object-reconstruction.md
    `-- scripts/
        |-- build_element_sheet_prompt.py
        |-- element_registry.py
        |-- pptx_object_helpers.js
        |-- split_transparent_sheet.py
        |-- validate_asset_decision_plan.py
        |-- validate_layout_plan.py
        |-- validate_media_refs.py
        `-- validate_pptx_integrity.py
```

## 环境要求

- Python 3.10+
- Pillow，用于拆分透明元素图
- Node.js，仅在 JavaScript PPTX 构建脚本中使用 `pptx_object_helpers.js` 时需要
- 实际组装 PPTX 时，需要配合 `pptxgenjs` 等 PPTX 生成工作流

安装 Python 依赖：

```bash
python -m pip install -r requirements.txt
```

## 校验示例

```bash
python ppt-image-to-editable/scripts/validate_asset_decision_plan.py examples/asset_decision_plan.example.json --slides 1
python ppt-image-to-editable/scripts/validate_layout_plan.py examples/layout_plan.example.json --strict
python ppt-image-to-editable/scripts/validate_pptx_integrity.py editable_output.pptx --strict
```

## 转换原则

这个 skill 避免简单地把整页截图塞进 PPT。目标是在视觉上接近源图片，同时提供尽可能有用的可编辑层：

1. 检查页面尺寸、页数，以及 PPT 是否为扁平图片。
2. 分类页面类型，如封面、目录、内容卡片、图表、表格、流程图、产品图页面等。
3. 先制作一个样页并等待确认。
4. 审核每一个非文字视觉元素。
5. 判断每个视觉元素应该裁剪、复用素材库、重新生成图片，还是用原生形状重建。
6. 先放置视觉图层，最后叠加可编辑文字图层。
7. 交付前运行校验。

## 校验工具

- `validate_asset_decision_plan.py`：确认每页都有完整的裁剪、素材库复用、图片生成或原生形状决策。
- `validate_layout_plan.py`：检查非整数字号、缺失换行策略、负数几何尺寸和不完整的形状元数据。
- `validate_media_refs.py`：检查构建脚本是否引用了不存在的图片。
- `validate_pptx_integrity.py`：检查生成的 PPTX 是否存在 XML、关系引用、媒体文件或几何尺寸问题。
- `split_transparent_sheet.py`：将透明元素图拆分为独立 PNG 素材。
- `element_registry.py`：管理整套 PPT 中可复用的视觉元素。
- `build_element_sheet_prompt.py`：根据资产决策计划生成批量图片生成提示。

## 仓库说明

生成的 PPT、预览图、本地页面图片和私有项目材料不应提交到 Git。实际转换时建议使用本地的 `outputs/`、`assets/` 或 `samples/` 目录。

