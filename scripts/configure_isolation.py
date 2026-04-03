#!/usr/bin/env python3
"""
配置Agent数据隔离级别
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 数据隔离类型定义
ISOLATION_TYPES = {
    "conversation_memory": "机器人对话记忆",
    "user_preferences": "用户偏好设置",
    "task_records": "任务记录、执行日志、任务状态",
    "session_context": "会话上下文、历史对话消息",
    "user_profile": "用户画像、私有业务数据",
    "temporary_state": "临时会话状态、缓存数据",
    "all": "所有数据类型"
}

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        return None

def save_config(config, config_path):
    """保存配置文件"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

def find_agent(config, agent_id):
    """查找Agent配置"""
    agents = config.get("agents", {}).get("list", [])
    for i, agent in enumerate(agents):
        if agent.get("id") == agent_id:
            return agent, i
    return None, -1

def configure_isolation(args):
    """配置数据隔离"""
    # 获取配置文件路径
    if args.config_path:
        config_path = Path(args.config_path)
    else:
        config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    # 加载配置文件
    config = load_config(config_path)
    if config is None:
        return 1
    
    # 查找Agent
    agent_config, agent_index = find_agent(config, args.agent_id)
    if agent_config is None:
        print(f"❌ 找不到Agent: {args.agent_id}")
        print("可用Agent列表:")
        agents = config.get("agents", {}).get("list", [])
        for agent in agents:
            print(f"  - {agent.get('id')} ({agent.get('name')})")
        return 1
    
    # 获取当前隔离配置
    if "dataIsolation" not in agent_config:
        agent_config["dataIsolation"] = {
            "enabled": False,
            "sharedTypes": []
        }
    
    # 解析隔离级别
    if args.isolation_level == "full":
        # 完全隔离
        agent_config["dataIsolation"]["enabled"] = False
        agent_config["dataIsolation"]["sharedTypes"] = []
        print(f"✅ 已为Agent '{args.agent_id}' 启用完全隔离")
        
    elif args.isolation_level == "partial":
        # 部分共享
        agent_config["dataIsolation"]["enabled"] = True
        
        # 使用用户指定的共享类型
        if args.shared_types:
            shared_types = args.shared_types
        else:
            # 如果没有指定，使用默认共享类型
            shared_types = ["conversation_memory", "user_preferences"]
        
        agent_config["dataIsolation"]["sharedTypes"] = shared_types
        
        print(f"✅ 已为Agent '{args.agent_id}' 启用部分共享")
        print("共享的数据类型:")
        for st in shared_types:
            if st in ISOLATION_TYPES:
                print(f"  - {ISOLATION_TYPES[st]}")
        
    elif args.isolation_level == "none":
        # 完全共享
        agent_config["dataIsolation"]["enabled"] = True
        agent_config["dataIsolation"]["sharedTypes"] = ["all"]
        print(f"✅ 已为Agent '{args.agent_id}' 启用完全共享")
    
    else:
        print(f"❌ 未知的隔离级别: {args.isolation_level}")
        print("可用级别: full（完全隔离）, partial（部分共享）, none（完全共享）")
        return 1
    
    # 更新session.dmScope
    if args.dm_scope:
        if "session" not in config:
            config["session"] = {}
        config["session"]["dmScope"] = args.dm_scope
        print(f"✅ 已设置session.dmScope为: {args.dm_scope}")
    
    # 保存配置文件
    if save_config(config, config_path):
        print(f"\n✅ 数据隔离配置已保存到: {config_path}")
        
        # 显示当前配置
        print("\n📋 当前隔离配置:")
        print(f"  Agent: {agent_config.get('name')} ({args.agent_id})")
        print(f"  隔离启用: {agent_config['dataIsolation']['enabled']}")
        
        if agent_config['dataIsolation']['enabled']:
            shared_types = agent_config['dataIsolation']['sharedTypes']
            if 'all' in shared_types:
                print("  共享类型: 所有数据类型")
            else:
                print(f"  共享类型: {len(shared_types)} 种类型")
                for st in shared_types:
                    if st in ISOLATION_TYPES:
                        print(f"    - {ISOLATION_TYPES[st]}")
        
        if "session" in config:
            print(f"  session.dmScope: {config['session'].get('dmScope')}")
        
        print("\n⚠️  需要重启OpenClaw Gateway使配置生效:")
        print("  openclaw gateway restart")
        
        return 0
    else:
        return 1

def interactive_mode(config_path):
    """交互式配置模式"""
    print("🤖 飞书多机器人数据隔离配置工具")
    print("=" * 50)
    
    # 加载配置文件
    config = load_config(config_path)
    if config is None:
        return 1
    
    # 显示Agent列表
    agents = config.get("agents", {}).get("list", [])
    if not agents:
        print("❌ 未找到Agent配置")
        return 1
    
    print("\n📋 可用的Agent:")
    for i, agent in enumerate(agents, 1):
        agent_id = agent.get("id")
        name = agent.get("name")
        default_str = " (默认)" if agent.get("default", False) else ""
        print(f"  {i}. {name}{default_str} [{agent_id}]")
    
    # 选择Agent
    try:
        choice = int(input("\n请选择要配置的Agent编号: ")) - 1
        if choice < 0 or choice >= len(agents):
            print("❌ 无效的选择")
            return 1
    except ValueError:
        print("❌ 请输入数字")
        return 1
    
    agent_config = agents[choice]
    agent_id = agent_config.get("id")
    
    # 显示当前隔离配置
    print(f"\n📊 Agent '{agent_config.get('name')}' 的当前配置:")
    if "dataIsolation" in agent_config:
        isolation = agent_config["dataIsolation"]
        enabled = isolation.get("enabled", False)
        shared_types = isolation.get("sharedTypes", [])
        
        print(f"  隔离启用: {enabled}")
        if enabled:
            if 'all' in shared_types:
                print("  共享类型: 所有数据类型")
            else:
                print(f"  共享类型: {len(shared_types)} 种类型")
                for st in shared_types:
                    if st in ISOLATION_TYPES:
                        print(f"    - {ISOLATION_TYPES[st]}")
    else:
        print("  隔离配置: 未设置")
    
    # 选择隔离级别
    print("\n🔒 请选择隔离级别:")
    print("  1. 完全隔离（默认，推荐）- 各机器人完全独立")
    print("  2. 部分共享 - 共享指定的数据类型")
    print("  3. 完全共享 - 所有数据完全共享")
    
    try:
        level_choice = int(input("请选择(1-3): "))
    except ValueError:
        print("❌ 请输入数字")
        return 1
    
    # 处理隔离级别
    if level_choice == 1:
        isolation_level = "full"
    elif level_choice == 2:
        isolation_level = "partial"
        
        # 选择要共享的数据类型
        print("\n📋 请选择要共享的数据类型（可多选）:")
        print("  1. 机器人对话记忆")
        print("  2. 用户偏好设置")
        print("  3. 任务记录、执行日志、任务状态")
        print("  4. 会话上下文、历史对话消息")
        print("  5. 用户画像、私有业务数据")
        print("  6. 临时会话状态、缓存数据")
        print("  7. 全部数据类型")
        
        try:
            type_choices = input("请输入编号（多个用逗号分隔）: ")
            type_indices = [int(x.strip()) for x in type_choices.split(",") if x.strip()]
        except ValueError:
            print("❌ 输入格式错误")
            return 1
        
        # 映射类型选择
        type_mapping = {
            1: "conversation_memory",
            2: "user_preferences",
            3: "task_records",
            4: "session_context",
            5: "user_profile",
            6: "temporary_state",
            7: "all"
        }
        
        shared_types = []
        for idx in type_indices:
            if idx in type_mapping:
                shared_type = type_mapping[idx]
                if shared_type == "all":
                    shared_types = ["all"]
                    break
                shared_types.append(shared_type)
        
        if not shared_types:
            shared_types = ["conversation_memory", "user_preferences"]
            print("⚠️  未选择共享类型，使用默认设置")
        
    elif level_choice == 3:
        isolation_level = "none"
        shared_types = ["all"]
    else:
        print("❌ 无效的选择")
        return 1
    
    # 配置隔离
    args = argparse.Namespace()
    args.config_path = str(config_path)
    args.agent_id = agent_id
    args.isolation_level = isolation_level
    args.shared_types = shared_types if level_choice == 2 else None
    args.dm_scope = None  # 保持原样
    
    return configure_isolation(args)

def main():
    parser = argparse.ArgumentParser(description="配置Agent数据隔离级别")
    parser.add_argument("--config-path", help="OpenClaw配置文件路径")
    parser.add_argument("--agent-id", required=True, help="要配置的Agent ID")
    parser.add_argument("--isolation-level", choices=["full", "partial", "none"], 
                       default="full", help="隔离级别: full(完全隔离), partial(部分共享), none(完全共享)")
    parser.add_argument("--shared-types", nargs="+", help="共享的数据类型（部分共享时使用）")
    parser.add_argument("--dm-scope", choices=["per-account-channel-peer", "per-channel-peer", "per-peer", "main"],
                       help="设置session.dmScope")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式配置模式")
    
    args = parser.parse_args()
    
    # 交互式模式
    if args.interactive:
        if args.config_path:
            config_path = Path(args.config_path)
        else:
            config_path = Path.home() / ".openclaw" / "openclaw.json"
        return interactive_mode(config_path)
    
    # 命令行模式
    return configure_isolation(args)

if __name__ == "__main__":
    sys.exit(main())