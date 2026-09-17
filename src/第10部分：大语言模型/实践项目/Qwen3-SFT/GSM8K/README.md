## 实验一

使用 `Qwen/Qwen3-1.7B-Base`，在单张 RTX 5090 上完成全参数 GSM8K response-only SFT，实现纯 PyTorch 单卡版


| 实验 | 内容                               | 作用     |
| ---- | ---------------------------------- | -------- |
| E0   | 未微调 Base 模型                   | 得到基线 |
| E1   | 正确的 response-only label masking | 主实验   |
| E2   | 不做 masking，对整段文本计算 loss  | 消融实验 |

GSM8K 的 `main` 配置包含 7473 条训练数据和 1319 条测试数据；每条数据有 `question` 和包含分步推理、最终 `#### 答案` 的 `answer`。


推荐划分：

- 原始 train：固定随机种子 42，拆成约 6973 条训练集和 500 条验证集。
- 原始 test：1319 条，项目结束时只评测最终模型。


| 阶段              | 你要做什么                                                         | 阶段产物与验收标准                                               |
| ----------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| 0. 定义实验       | 确定 Base 模型、prompt 格式、数据划分、指标和随机种子              | 写出一页实验设计，训练前不再随意改变评测规则                     |
| 1. 环境验证       | 检查 PyTorch、CUDA、5090、BF16、Transformers 和模型加载            | 能加载 tokenizer/model，并对一个 prompt 完成 forward 与 generate |
| 2. 探索数据       | 加载 GSM8K，检查字段、异常样本、答案格式和 token 长度分布          | 知道 P50/P95/最大长度，据此选择 max_length                       |
| 3. 数据预处理     | 实现 prompt 构造、分段 tokenize、EOS、截断和 label masking         | 随机打印 5 条样本，所有 prompt label 都是`-100`                |
| 4. 动态 Collator  | 按 batch 最长样本 padding；构造 input_ids、attention_mask、labels  | 三个张量尺寸一致；pad id、mask、label padding 均正确             |
| 5. 最小正确性实验 | 只用 8～32 条数据反复训练，检查 loss 是否快速下降                  | 能明显过拟合小数据，并生成接近训练答案的结果                     |
| 6. 手写训练循环   | 实现 forward、loss、backward、累积梯度、裁剪、optimizer、scheduler | 能稳定运行数百步，无 NaN、无显存持续增长                         |
| 7. 验证流程       | 实现 validation loss 和生成式 exact match                          | eval 时使用 prompt-only 输入，不把标准答案喂给模型               |
| 8. Checkpoint     | 保存模型、tokenizer、optimizer、scheduler、step、epoch、随机状态   | 中断后恢复训练，学习率和 global step 连续                        |
| 9. 正式实验       | 跑 E0/E1/E2，记录配置、显存、吞吐量和指标                          | 得到可复现结果表和 loss 曲线                                     |
