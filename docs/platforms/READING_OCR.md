# 阅读摘录 OCR 校对

用 Python 3.12+ 在 macOS 或 Linux 运行，无需安装 Python 第三方库。输入为 UTF-8 纯文本，例如从印象笔记复制出的阅读摘录。脚本保留原文，另存草稿和带行列坐标的逐字改动报告。

## 先用合成示例验证

从仓库根目录运行以下命令。示例会补上句首的「海」，并将「神经可朔性」改成「神经可塑性」。这两条是演示规则，通用语义校对需要显式选择模型。

```sh
python3 scripts/reading_ocr/ocr_audit.py --demo
python3 -m unittest discover -s scripts/reading_ocr
```

## 验证批处理

从仓库根目录用合成文本运行两次。首次应得到 `processed: 1` 和 `draft_edits: 2`。第二次应得到 `unchanged: 1`，输入文件保留原文。

```sh
ocr_test="$(mktemp -d "${TMPDIR:-/tmp}/reading-ocr.XXXXXX")"
mkdir "$ocr_test/inbox"
printf '%s\n' '马体参与记忆形成。' '神经可朔性也与学习有关。' > "$ocr_test/inbox/sample.txt"
python3 scripts/reading_ocr/ocr_batch.py --root "$ocr_test"
python3 scripts/reading_ocr/ocr_batch.py --root "$ocr_test"
```

## 设置周期任务

```sh
ocr_data="$HOME/reading-ocr"
(umask 077; mkdir -p "$ocr_data/inbox")
# 将已有的 UTF-8 .txt 摘录放在 inbox/，再运行批处理。
python3 scripts/reading_ocr/ocr_batch.py --root "$ocr_data"
```

批处理读取 `inbox/*.txt`，逐份报告保存到 `reports/`，汇总保存到 `latest-summary.json`。再次运行时跳过正文、规则和模型配置均未变化的文件。有文件失败时，仍处理其他文件，并返回非零退出状态。可用系统调度器或支持执行本地命令的任务工具按需运行，例如每周一次。为任务填写解释器、脚本和数据目录的绝对路径，并在相同运行身份下先手动验证。任务只读取或汇报汇总数字，逐份报告留在本地。

可以在数据目录加一份 `rules.json`，格式为 JSON 数组。每项包含 `before` 和 `after`，两者只能相差一个汉字的增加、删除或替换。`line_start: true` 将规则限制在行首。多个规则位置冲突时，草稿保留该处原文。

批处理默认离线。加 `--ollama-model 模型名` 可将文字交给本机 Ollama 生成语义建议。单篇也可用 `ocr_audit.py --file 路径 --output 报告路径`，或从标准输入读取。单篇显式开启 `--engine deepseek` 并配置 `DEEPSEEK_API_KEY` 时，会将摘录文字发送给 DeepSeek。模型建议仅保存在报告里，草稿中的自动修改来自规则。

摘录、报告、私用规则和凭据都应保存在仓库外。这一步的输入已经是文本。印象笔记导入、书目关联和平台写回属于后续接入。
