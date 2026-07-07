# packing-list-generator

QoderWork 行李清单生成器技能。根据目的地天气、行程天数、出行类型和人员构成，生成个性化可勾选行李清单 HTML，含分类清单、按天穿搭建议、临走前待办，支持打印、保存图片、文本复制；覆盖国内/国际出行与多城市行程。

## 触发场景

用户提到「行李清单 / 打包清单 / 旅行清单 / 出差准备 / packing list」或描述「去某地几天要带什么 / 出门带什么 / 帮我打包」等出行物品询问时。

**不触发**：采购、装修、进货、备货、婚礼、月子、食材等非出行场景。

## 安装

在 QoderWork 中执行：

```
/skill add michelleipad/packing-list-generator
```

或手动 clone 到本地技能目录：

```bash
git clone https://github.com/michelleipad/packing-list-generator ~/.qoder/skills/packing-list-generator
```

## 目录结构

```
SKILL.md                 # 主入口与触发描述
package.json             # 元数据
assets/templates/        # HTML 模板（head / body-skeleton / tail / template）
references/              # 分层规则文档（执行模式 / 天气 API / 区域套件 / 打包规则等）
scripts/                 # 校验与拼装脚本
evals/                   # 评测用例
```

## 依赖 API

- Open-Meteo Geocoding API (`geocoding-api.open-meteo.com`)
- Open-Meteo Forecast API (`api.open-meteo.com`)

均为免费公开 API，无需 Key。

## 版本

当前版本 0.4.0，见 `SKILL.md` frontmatter。
