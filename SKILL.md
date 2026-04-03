---
name: feishu-multi-bot-config
description: "管理OpenClaw飞书多机器人配置，实现多机器人与Agent绑定、Skill权限共享、数据隔离控制。当用户需要：配置多个飞书机器人对应不同Agent、设置Skill和权限共享、控制机器人对话记忆/任务日志/会话上下文/用户画像的隔离级别、管理飞书账户与Agent路由绑定时使用此技能。"
version: 1.0.0
official: true
---

# 飞书多机器人配置管理技能

管理OpenClaw飞书多机器人配置，实现多机器人与Agent绑定、Skill和权限自动共享、数据隔离控制。

## 核心功能

### 1. 多机器人配置
- 在OpenClaw配置中添加多个飞书机器人账户
- 每个账户绑定到不同的Agent
- 自动生成Agent配置和路由绑定

### 2. Skill和权限共享
- 默认自动共享该Agent下的所有Skill
- 支持配置共享的权限范围
- 提供一键启用/禁用共享

### 3. 数据隔离控制
- **默认关闭隔离**：各机器人独立运行，完全隔离
- **可选开启隔离**：控制以下数据类型的共享：
  - 机器人对话记忆
  - 用户偏好设置
  - 任务记录、执行日志、任务状态
  - 会话上下文、历史对话消息
  - 用户画像、私有业务数据
  - 临时会话状态、缓存数据

## 使用场景

### 场景1：配置多飞书机器人对应不同Agent

用户输入示例：
```
配置3个飞书机器人，分别对应客服、销售、技术Agent
```

执行流程：
1. 读取当前`openclaw.json`配置
2. 检查`channels.feishu.accounts`配置
3. 生成3个飞书账户配置
4. 配置3个Agent配置
5. 创建绑定规则路由到对应Agent
6. 自动共享每个Agent的Skill和权限
7. 生成完整配置供用户审核

### 场景2：启用Skill和权限共享

用户输入示例：
```
启用客服Agent的Skill和权限共享
```

执行流程：
1. 读取客服Agent配置
2. 查询该Agent下的所有Skill列表
3. 配置共享策略（默认全部共享）
4. 更新`openclaw.json`
5. 重启OpenClaw使配置生效

### 场景3：设置数据隔离级别

用户输入示例：
```
开启数据隔离，但共享对话记忆和用户偏好
```

执行流程：
1. 选择要隔离的数据类型
2. 配置隔离级别（完全隔离/部分共享/完全共享）
3. 更新`session.dmScope`和隔离配置
4. 生成隔离策略文档
5. 应用配置并验证

### 场景4：管理飞书账户与Agent路由绑定

用户输入示例：
```
将ou_12345绑定为销售Agent，将oc_group_xxx绑定为客服Agent
```

执行流程：
1. 读取当前绑定配置
2. 解析用户指定的绑定规则
3. 添加或更新绑定配置
4. 验证绑定规则的有效性
5. 保存配置并重启Gateway

## 配置说明

### OpenClaw配置结构

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
          "enabled": false,
          "sharedTypes": [
            "conversation_memory",
            "user_preferences"
          ]
        }
      },
      {
        "id": "sales",
        "name": "销售Agent",
        "workspace": "~/.openclaw/workspace-sales",
        "model": {"primary": "ark/doubao"},
        "sharedSkills": true,
        "sharedPermissions": true,
        "dataIsolation": {
          "enabled": false,
          "sharedTypes": []
        }
      }
    ]
  },
  "session": {
    "dmScope": "per-account-channel-peer"
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "threadSession": true,
      "replyMode": "auto",
      "accounts": {
        "customer-service": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "botName": "客服机器人",
          "dmPolicy": "allowlist",
          "allowFrom": ["ou_5b990e213988b9bcf396f955a50b2a22"]
        },
        "sales": {
          "appId": "cli_yyy",
          "appSecret": "yyy",
          "botName": "销售机器人",
          "dmPolicy": "open",
          "allowFrom": ["*"]
        }
      },
      "groups": {
        "*": {"requireMention": true}
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
    },
    {
      "agentId": "sales",
      "match": {
        "channel": "feishu",
        "accountId": "sales"
      }
    }
  ]
}
```

### 隔离级别选项

#### 完全隔离（默认）
- `dataIsolation.enabled: false`
- `session.dmScope: "per-account-channel-peer"`
- 各机器人完全独立，互不共享任何数据

#### 部分共享
- `dataIsolation.enabled: true`
- `dataIsolation.sharedTypes: ["conversation_memory", "user_preferences"]`
- 只共享指定的数据类型

#### 完全共享
- `dataIsolation.enabled: true`
- `dataIsolation.sharedTypes: ["all"]`
- 所有数据类型完全共享

## 命令行工具

### 飞书账户配置
```bash
# 查看当前飞书账户配置
python scripts/list_feishu_accounts.py

# 查看Agent绑定规则
python scripts/list_bindings.py

# 查看隔离配置
python scripts/list_isolation.py
```

### 配置管理
```bash
# 创建新的多机器人配置
python scripts/setup_multi_bot.py --agent-customer-service --agent-sales --agent-technical

# 启用Skill共享
python scripts/enable_skill_share.py --agent-id customer-service

# 配置数据隔离
python scripts/configure_isolation.py --agent-id customer-service --shared-types conversation_memory --shared-types user_preferences

# 查看隔离策略文档
python scripts/show_isolation_policy.py --agent-id customer-service
```

### 实用工具
```bash
# 生成隔离配置示例
python scripts/generate_isolation_examples.py

# 验证配置文件
python scripts/validate_config.py --config-path ~/.openclaw/openclaw.json

# 应用配置并重启
python scripts/apply_and_restart.py
```

## 使用流程

### 首次配置多机器人

1. **收集信息**
   - Agent数量和名称
   - 每个Agent需要绑定的飞书账户信息
   - 每个账户的Bot名称
   - 是否需要Skill/权限共享

2. **执行配置**
   ```bash
   python scripts/setup_multi_bot.py \
     --agent-customer-service \
     --agent-sales \
     --agent-technical \
     --shared-skills
   ```

3. **配置飞书应用**
   - 在飞书开放平台创建3个应用
   - 获取App ID和App Secret
   - 配置权限和事件回调

4. **保存配置**
   - 自动生成配置文件
   - 备份当前配置
   - 应用新配置

5. **验证功能**
   ```bash
   openclaw channels list
   openclaw agents bindings
   openclaw logs --follow
   ```

### 管理隔离级别

1. **选择Agent**
   ```
   老大，需要配置哪个Agent的隔离级别？
   - customer-service（客服Agent）
   - sales（销售Agent）
   - technical（技术Agent）
   ```

2. **选择隔离级别**
   ```
   请选择隔离级别：
   1. 完全隔离（默认，推荐）
   2. 部分共享（共享指定数据）
   3. 完全共享（所有数据共享）
   ```

3. **配置共享类型（部分共享）**
   ```
   需要共享哪些数据类型？
   - 机器人对话记忆
   - 用户偏好设置
   - 任务记录、执行日志、任务状态
   - 会话上下文、历史对话消息
   - 用户画像、私有业务数据
   - 临时会话状态、缓存数据
   ```

4. **应用配置**
   - 更新`openclaw.json`
   - 重启OpenClaw Gateway
   - 验证配置生效

## 注意事项

1. **配置备份**：每次修改配置前自动备份
2. **配置验证**：修改后自动验证配置文件有效性
3. **服务重启**：配置修改后自动重启Gateway使配置生效
4. **数据迁移**：启用隔离时，现有数据不会被清除，但新数据遵循隔离规则
5. **权限管理**：每个飞书账户需要单独配置权限范围
6. **路由绑定**：确保每个Agent都有正确的路由绑定

## 故障排查

### 飞书连接失败
1. 检查App ID和App Secret是否正确
2. 验证飞书应用是否已审核通过
3. 确认事件回调URL是否正确配置

### Agent绑定失败
1. 检查`bindings`配置是否正确
2. 验证`accountId`与`accounts`中的key是否匹配
3. 确认Agent ID存在

### 隔离配置未生效
1. 检查`session.dmScope`配置
2. 验证`dataIsolation.enabled`是否为`true`
3. 确认`sharedTypes`配置正确
4. 检查Gateway是否已重启

## 依赖项

- Python 3.8+
- python-docx（读取配置文档）
- OpenClaw CLI（命令行工具）
- JSON解析和验证

## 输出格式

- 配置文件：`openclaw.json`
- 隔离策略文档：`isolation-policy-<agent-id>.md`
- 配置备份：`openclaw.json.backup-<timestamp>`
- 日志文件：`feishu-multi-bot-config.log`

## 快速开始

### 1分钟快速配置

```bash
# 配置2个飞书机器人对应2个Agent
python scripts/setup_multi_bot.py --agent-sales --agent-cs --shared-skills

# 查看配置
python scripts/list_feishu_accounts.py
python scripts/list_bindings.py

# 启用数据隔离（客服Agent）
python scripts/configure_isolation.py --agent-id cs --isolation-level per-account

# 应用配置并重启
python scripts/apply_and_restart.py
```

### 验证配置

```bash
# 检查飞书账户状态
openclaw channels list

# 查看Agent绑定
openclaw agents bindings

# 查看Gateway状态
openclaw gateway status

# 实时日志
openclaw logs --follow
```

## 文档参考

- OpenClaw官方文档：https://docs.openclaw.ai
- 飞书开放平台：https://open.feishu.cn/document
- 配置示例：`examples/`目录下
