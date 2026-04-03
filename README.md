# 飞书多机器人配置管理技能

这是一个OpenClaw技能，用于管理飞书多机器人配置，实现多机器人与Agent绑定、Skill权限共享、数据隔离控制。

## 功能特性

### 🚀 核心功能
- **多机器人配置**：在OpenClaw中配置多个飞书机器人账户
- **Agent绑定**：每个机器人绑定到不同的Agent
- **Skill共享**：自动共享Agent下的所有Skill和权限
- **数据隔离**：灵活控制数据共享级别

### 🔒 数据隔离控制
支持三种隔离级别：
1. **完全隔离（默认）**：各机器人完全独立，互不共享任何数据
2. **部分共享**：只共享指定的数据类型
3. **完全共享**：所有数据类型完全共享

### 📊 可共享的数据类型
- 机器人对话记忆
- 用户偏好设置  
- 任务记录、执行日志、任务状态
- 会话上下文、历史对话消息
- 用户画像、私有业务数据
- 临时会话状态、缓存数据

## 安装和使用

### 1. 快速开始
```bash
# 配置3个飞书机器人对应3个Agent
python scripts/setup_multi_bot.py --agent-customer-service --agent-sales --agent-technical

# 查看配置
python scripts/list_feishu_accounts.py
python scripts/list_bindings.py

# 启用数据隔离
python scripts/configure_isolation.py --agent-id customer-service --isolation-level partial --shared-types conversation_memory --shared-types user_preferences

# 应用配置并重启
python scripts/apply_and_restart.py
```

### 2. 交互式配置
```bash
# 交互式配置数据隔离
python scripts/configure_isolation.py --interactive

# 验证配置文件
python scripts/validate_config.py --config-path ~/.openclaw/openclaw.json
```

## 命令行工具

### 配置管理
| 工具 | 功能 |
|------|------|
| `setup_multi_bot.py` | 创建多机器人配置 |
| `configure_isolation.py` | 配置数据隔离级别 |
| `apply_and_restart.py` | 应用配置并重启Gateway |

### 查看工具
| 工具 | 功能 |
|------|------|
| `list_feishu_accounts.py` | 查看飞书账户配置 |
| `list_bindings.py` | 查看绑定规则 |
| `list_isolation.py` | 查看数据隔离配置 |
| `validate_config.py` | 验证配置文件 |

### 实用工具
| 工具 | 功能 |
|------|------|
| `show_isolation_policy.py` | 显示隔离策略文档 |
| `generate_isolation_examples.py` | 生成隔离配置示例 |

## 配置示例

### 1. 基础配置
```bash
# 创建3个Agent：客服、销售、技术
python scripts/setup_multi_bot.py \
  --agent-customer-service \
  --agent-sales \
  --agent-technical \
  --shared-skills
```

### 2. 配置数据隔离
```bash
# 客服Agent：部分共享（共享对话记忆和用户偏好）
python scripts/configure_isolation.py \
  --agent-id customer-service \
  --isolation-level partial \
  --shared-types conversation_memory \
  --shared-types user_preferences

# 销售Agent：完全隔离
python scripts/configure_isolation.py \
  --agent-id sales \
  --isolation-level full

# 技术Agent：完全共享
python scripts/configure_isolation.py \
  --agent-id technical \
  --isolation-level none
```

### 3. 应用配置
```bash
# 验证配置文件
python scripts/validate_config.py --config-path ~/.openclaw/openclaw.json

# 应用配置并重启
python scripts/apply_and_restart.py
```

## 配置说明

### OpenClaw配置文件结构
```json
{
  "agents": {
    "list": [
      {
        "id": "customer-service",
        "name": "客服Agent",
        "default": true,
        "workspace": "~/.openclaw/workspace-cs",
        "model": {"primary": "ark/gpt-4"},
        "sharedSkills": true,
        "sharedPermissions": true,
        "dataIsolation": {
          "enabled": false,  // 完全隔离
          "sharedTypes": []
        }
      }
    ]
  },
  "session": {
    "dmScope": "per-account-channel-peer"  // 按账户+渠道+用户隔离
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "accounts": {
        "customer-service": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "botName": "客服机器人"
        }
      }
    }
  },
  "bindings": [
    {
      "agentId": "customer-service",
      "match": {
        "channel": "feishu",
        "accountId": "customer-service"
      }
    }
  ]
}
```

### 隔离级别说明

#### 完全隔离（默认）
```json
"dataIsolation": {
  "enabled": false,
  "sharedTypes": []
}
```
- 各机器人完全独立运行
- 不共享任何数据
- 适合需要严格数据隔离的场景

#### 部分共享
```json
"dataIsolation": {
  "enabled": true,
  "sharedTypes": ["conversation_memory", "user_preferences"]
}
```
- 只共享指定的数据类型
- 其他数据保持隔离
- 适合需要部分数据共享的场景

#### 完全共享
```json
"dataIsolation": {
  "enabled": true,
  "sharedTypes": ["all"]
}
```
- 所有数据类型完全共享
- 机器人之间完全透明
- 适合紧密协作的场景

## 使用场景

### 场景1：企业多部门机器人
- **客服机器人**：完全隔离，保护用户隐私
- **销售机器人**：部分共享，共享客户偏好
- **技术机器人**：完全隔离，保护技术数据

### 场景2：多渠道客服系统
- **微信客服**：完全隔离
- **飞书客服**：部分共享（共享对话历史）
- **网页客服**：完全共享（统一用户画像）

### 场景3：多语言支持
- **中文客服**：完全隔离
- **英文客服**：部分共享（共享用户信息）
- **多语言翻译**：完全共享

## 最佳实践

### 1. 安全建议
- 敏感数据使用完全隔离
- 非敏感数据可使用部分共享
- 定期审查共享配置

### 2. 性能建议
- 数据隔离会增加内存使用
- 完全共享性能最好
- 完全隔离资源消耗最大

### 3. 维护建议
- 修改配置前先备份
- 使用验证工具检查配置
- 修改后重启Gateway

## 故障排除

### 常见问题

#### 1. 飞书连接失败
```bash
# 检查飞书应用配置
python scripts/list_feishu_accounts.py

# 检查App ID和App Secret是否正确
# 确认飞书应用已审核通过
```

#### 2. Agent绑定失败
```bash
# 检查绑定规则
python scripts/list_bindings.py

# 验证Agent ID是否正确
# 检查账户ID是否匹配
```

#### 3. 隔离配置未生效
```bash
# 检查隔离配置
python scripts/list_isolation.py

# 验证session.dmScope配置
# 确认Gateway已重启
```

#### 4. 配置文件错误
```bash
# 验证配置文件
python scripts/validate_config.py --config-path ~/.openclaw/openclaw.json

# 备份并修复
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup
python scripts/setup_multi_bot.py --agent-main
```

### 监控和日志
```bash
# 实时日志
openclaw logs --follow

# Gateway状态
openclaw gateway status

# 健康检查
openclaw doctor
```

## 依赖项

- Python 3.8+
- OpenClaw CLI
- 飞书开放平台账户

## 文件结构
```
feishu-multi-bot-config/
├── SKILL.md                    # 技能定义文件
├── README.md                   # 说明文档
├── scripts/                    # 工具脚本
│   ├── setup_multi_bot.py      # 多机器人配置
│   ├── configure_isolation.py  # 隔离配置
│   ├── apply_and_restart.py    # 应用配置
│   ├── list_feishu_accounts.py # 查看账户
│   ├── list_bindings.py        # 查看绑定
│   ├── list_isolation.py       # 查看隔离
│   └── validate_config.py      # 验证配置
└── examples/                   # 配置示例
    ├── basic-config.json       # 基础配置
    └── isolation-examples.md   # 隔离示例
```

## 支持

如有问题，请：
1. 检查配置文件是否正确
2. 查看OpenClaw日志
3. 使用验证工具检查配置
4. 参考示例配置文件

## 许可证

MIT License