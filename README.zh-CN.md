# Apple App Review 2.5.19 — 隐藏功能排查 Skill

[English](README.md) | [简体中文](README.zh-CN.md)

一个可复用的 Agent Skill，针对 **Apple App Review Guideline 2.5.19** 中的**隐藏、休眠及未说明功能**进行排查，适用于原生 iOS、Flutter 和 React Native 项目。

帮助你区分正式业务与内部测试能力，保留正常功能、记录例外，并验证实际发布产物。附带只读、无第三方依赖的 Python 归档扫描器。

**这是独立社区项目，与 Apple 无关联，也未获 Apple 背书。它提供工程排查方法，不保证审核通过，也不用于向审核隐藏功能。** 最新要求以 [Apple 官方审核指南](https://developer.apple.com/app-store/review/guidelines/#software-requirements) 为准。

## 覆盖范围

- 按风险优先级排查内部工具、购买覆盖、模拟数据、隐藏入口和远端配置。
- 覆盖原生 target、生成协议、共享依赖、各语言 strings 和打包资源的编译隔离。
- 明确 Debug、完整内测 Release、正式候选、TestFlight、App Store 和 Android 的能力差异。
- 检查精简工具权限、直接路由、启动等待、临时错误、历史设置与升级兼容。
- 按真实业务语义命名、迁移版本化配置，不以改名掩盖功能，不破坏旧客户端。
- 补充 StoreKit 购买测试、真实购买代码的正向检查，以及上传前归档扫描阻断。
- 提供远端功能清单、审核访问与上线计划、项目专用扫描策略和交接模板。

**TestFlight 是安装渠道，不是编译配置。** 同一候选构建经 TestFlight 安装或提交商店，其已编译能力相同；通过收据限制访问不等于代码已从包中移除。

## 安装

Codex 用户可将仓库克隆到 skills 目录。如果目标目录已存在，请先检查原技能，不要直接覆盖。

```sh
git clone https://github.com/sinyu1012/ios-hidden-feature-audit.git   "${CODEX_HOME:-$HOME/.codex}/skills/ios-hidden-feature-audit"
```

必要时刷新技能列表或开启新会话。其他支持 `SKILL.md` 的 Agent 可将完整目录放到其规定的技能位置；也可以手动阅读文档、运行扫描器。

## 使用示例

```text
使用 $ios-hidden-feature-audit 按 Apple App Review Guideline 2.5.19
排查当前 iOS 项目，先不改代码。覆盖原生代码和全部国际化资源，
给出证据、分发矩阵和按风险排序的修改方案。
```

```text
使用 $ios-hidden-feature-audit 按已确定方案，将内部测试能力从正式候选中
编译排除，保留完整内测 Release 和 Android 原有行为。
只做代码层面验证，不打包、不启动模拟器或真机。
```

技能遵循本次任务的授权边界。执行排查不代表获得发布、上传构建或修改生产配置的授权。

## 扫描归档

使用 Python 3.9 或更新版本；脚本只依赖标准库，无需 Xcode。输入必须是**未加密**的 `.app`，或只有一个主 App 的 `.xcarchive`。IPA 需先单独解包。

```sh
# 仅列线索清单：退出 0 不代表合规或通过项目策略。
python3 scripts/scan_bundle.py /path/to/Example.app

# 复制后替换为本项目的稳定标识与资源路径。
cp assets/audit-policy.example.json /path/to/project-policy.json
# 编辑策略并移除 example_only 后执行：
python3 scripts/scan_bundle.py /path/to/Example.xcarchive   --policy /path/to/project-policy.json --profile app-store
```

未适配的示例策略会被拒绝执行；它不是 Apple 关键词黑名单。

| 退出码 | 含义 |
|---|---|
| 0 | 清单完成或项目策略通过；需查看 `mode` / `status` |
| 1 | 命中项目禁止项，或缺少要求存在的证据 |
| 2 | 输入、策略、解析、大小限制或扫描错误 |

脚本通过 magic bytes 识别 Mach-O，扫描支持的资源，并同时支持禁止项和必须保留项。`debug`、`mock`、`purchase` 等泛词仅是排查线索。未命中不证明功能不存在，命中也不证明功能可执行或一定被拒。详见 [扫描说明与限制](references/artifact-scanning.md)。

扫描器不会上传二进制或报告，也不输出原始匹配上下文。但文件名、配置中的标识及配置错误中的路径仍可能敏感，分享报告前必须脱敏。

## 目录导航

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | Agent 工作流入口 |
| [政策与证据](references/policy-and-evidence.md) | 官方依据与证据边界 |
| [实施要点](references/implementation.md) | 编译隔离、运行时访问、配置迁移 |
| [提交检查](references/submission-checks.md) | StoreKit 测试、正式购买保留、发布 CI 与远端功能披露 |
| [项目模板](references/project-templates.md) | 能力矩阵、AGENTS.md、测试与审核备注 |
| [产物扫描](references/artifact-scanning.md) | 策略格式与扫描限制 |
| [示例策略](assets/audit-policy.example.json) | 必须适配后才能使用的模板 |

技能正文和技术参考默认使用英文；本 README 提供中文介绍与使用说明。

## 验证与贡献

```sh
python3 -m unittest discover -s tests -v
```

测试使用合成 bundle，不编译或启动真实 iOS App；验证的是扫描器行为，不能证明审核合规。CI 在 Python 3.9 和 3.13 上运行测试。

欢迎提交 issue 和 PR。请只提供脱敏后的最小复现，不提交私有应用标识、凭据、个人数据、内部网址、业务二进制或未脱敏扫描报告。涉及政策的结论应引用最新 Apple 官方资料，并区分证据与推断。

## 许可证

[MIT](LICENSE)。
