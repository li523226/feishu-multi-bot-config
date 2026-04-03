#!/usr/bin/env python3
"""
设置OpenClaw多飞书机器人配置
"""

import json
import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime

def backup_config(config_path):
    """备份配置文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = config_path.parent / f"{config_path.name}.backup-{timestamp}"
    
    try:
        shutil.copy2(config_path, backup_path)
        print(f"✅ 配置文件已备份至: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  备份失败: {e}")
        return None

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {config_path}")
        print("正在创建新配置文件...")
        return create_new_config()
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return None

def create_new_config():
    """创建新的配置文件"""
    return {
        "version": "1.0.0",
        "agents": {
            "list": []
        },
        "session": {
            "dmScope": "per-account-channel-peer"
        },
        "channels": {},
        "bindings": []
    }

def save_config(config, config_path):
    """保存配置文件"""
    try:
        # 创建父目录
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 配置文件已保存: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

def get_agent_template(agent_id, name, model="ark/doubao", shared_skills=True):
    """获取Agent配置模板"""
    return {
        "id": agent_id,
        "name": name,
        "default": False,
        "workspace": f"~/.openclaw/workspace-{agent_id}",
        "model": {
            "primary": model
        },
        "sharedSkills": shared_skills,
        "sharedPermissions": shared_skills,
        "dataIsolation": {
            "enabled": False,
            "sharedTypes": []
        }
    }

def get_feishu_account_template(account_id, bot_name, app_id=None, app_secret=None):
    """获取飞书账户配置模板"""
    return {
        "appId": app_id or f"cli_{account_id}_placeholder",
        "appSecret": app_secret or f"secret_{account_id}_placeholder",
        "botName": bot_name,
        "dmPolicy": "allowlist",
        "allowFrom": ["*"]
    }

def setup_multi_bot(args):
    """设置多机器人配置"""
    # 获取配置文件路径
    if args.config_path:
        config_path = Path(args.config_path)
    else:
        config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    # 备份配置文件
    backup_config(config_path)
    
    # 加载配置文件
    config = load_config(config_path)
    if config is None:
        return 1
    
    # 确保必要的配置项存在
    if "agents" not in config:
        config["agents"] = {"list": []}
    if "channels" not in config:
        config["channels"] = {}
    if "bindings" not in config:
        config["bindings"] = []
    
    # 配置飞书通道
    if "feishu" not in config["channels"]:
        config["channels"]["feishu"] = {
            "enabled": True,
            "threadSession": True,
            "replyMode": "auto",
            "accounts": {},
            "groups": {
                "*": {"requireMention": True}
            }
        }
    
    # 解析Agent参数
    agents = []
    if args.agent_customer_service:
        agents.append(("customer-service", "客服Agent"))
    if args.agent_sales:
        agents.append(("sales", "销售Agent"))
    if args.agent_technical:
        agents.append(("technical", "技术Agent"))
    if args.agent_support:
        agents.append(("support", "支持Agent"))
    if args.agent_main:
        agents.append(("main", "主Agent", True))  # 设置为主Agent
    
    # 如果没有指定Agent，使用默认配置
    if not agents:
        agents = [
            ("customer-service", "客服Agent"),
            ("sales", "销售Agent"),
            ("technical", "技术Agent")
        ]
    
    print(f"🔄 正在配置 {len(agents)} 个Agent...")
    
    # 更新Agent配置
    agent_ids = []
    for agent_info in agents:
        if len(agent_info) == 3:
            agent_id, name, is_default = agent_info
        else:
            agent_id, name = agent_info
            is_default = False
        
        # 检查Agent是否已存在
        existing_agent = None
        for agent in config["agents"]["list"]:
            if agent["id"] == agent_id:
                existing_agent = agent
                break
        
        if existing_agent:
            print(f"ℹ️  Agent '{name}' ({agent_id}) 已存在，跳过创建")
        else:
            agent_config = get_agent_template(agent_id, name)
            if is_default:
                agent_config["default"] = True
            config["agents"]["list"].append(agent_config)
            print(f"✅ 创建Agent: {name} ({agent_id})")
        
        agent_ids.append(agent_id)
    
    # 确保有默认Agent
    has_default = any(agent.get("default", False) for agent in config["agents"]["list"])
    if not has_default and config["agents"]["list"]:
        config["agents"]["list"][0]["default"] = True
        print(f"⚠️  未指定默认Agent，将第一个Agent '{config['agents']['list'][0]['name']}' 设为默认")
    
    # 更新飞书账户配置
    feishu_accounts = config["channels"]["feishu"].get("accounts", {})
    
    for agent_id in agent_ids:
        if agent_id not in feishu_accounts:
            bot_name = f"{agent_id.capitalize()}机器人"
            account_config = get_feishu_account_template(agent_id, bot_name)
            feishu_accounts[agent_id] = account_config
            print(f"✅ 创建飞书账户: {bot_name} (账户ID: {agent_id})")
    
    config["channels"]["feishu"]["accounts"] = feishu_accounts
    
    # 更新绑定规则
    existing_bindings = config.get("bindings", [])
    
    for agent_id in agent_ids:
        # 检查是否已有绑定规则
        binding_exists = False
        for binding in existing_bindings:
            if (binding.get("agentId") == agent_id and 
                binding.get("match", {}).get("channel") == "feishu" and
                binding.get("match", {}).get("accountId") == agent_id):
                binding_exists = True
                break
        
        if not binding_exists:
            binding = {
                "agentId": agent_id,
                "match": {
                    "channel": "feishu",
                    "accountId": agent_id
                }
            }
            existing_bindings.append(binding)
            print(f"✅ 创建绑定规则: {agent_id} -> 飞书账户 {agent_id}")
    
    config["bindings"] = existing_bindings
    
    # 保存配置文件
    if save_config(config, config_path):
        print("\n🎉 配置完成！")
        print("\n配置摘要：")
        print("-" * 40)
        
        # 显示Agent列表
        print("📋 Agent配置：")
        for agent in config["agents"]["list"]:
            default_str = " (默认)" if agent.get("default", False) else ""
            print(f"  - {agent['name']} ({agent['id']}){default_str}")
        
        # 显示飞书账户
        print("\n🤖 飞书机器人：")
        for account_id, account in feishu_accounts.items():
            print(f"  - {account['botName']} (账户ID: {account_id})")
        
        # 显示绑定规则
        print("\n🔗 绑定规则：")
        feishu_bindings = [b for b in config["bindings"] if b.get("match", {}).get("channel") == "feishu"]
        for binding in feishu_bindings:
            print(f"  - {binding['agentId']} -> 飞书账户 {binding['match']['accountId']}")
        
        print("\n" + "=" * 40)
        print("⚠️  重要提示：")
        print("1. 请将配置文件中的 App ID 和 App Secret 替换为真实的飞书应用凭证")
        print("2. 每个飞书应用需要在飞书开放平台单独创建")
        print("3. 配置完成后需要重启OpenClaw Gateway")
        print(f"4. 原始配置已备份至: {config_path}.backup-*")
        
        # 生成重启命令
        print("\n🔄 重启命令：")
        print("  openclaw gateway restart")
        
        return 0
    else:
        return 1

def main():
    parser = argparse.ArgumentParser(description="设置OpenClaw多飞书机器人配置")
    parser.add_argument("--config-path", help="OpenClaw配置文件路径")
    parser.add_argument("--agent-customer-service", action="store_true", help="创建客服Agent")
    parser.add_argument("--agent-sales", action="store_true", help="创建销售Agent")
    parser.add_argument("--agent-technical", action="store_true", help="创建技术Agent")
    parser.add_argument("--agent-support", action="store_true", help="创建支持Agent")
    parser.add_argument("--agent-main", action="store_true", help="创建主Agent（设为默认）")
    parser.add_argument("--shared-skills", action="store_true", default=True, help="启用Skill共享（默认启用）")
    
    args = parser.parse_args()
    return setup_multi_bot(args)

if __name__ == "__main__":
    sys.exit(main())