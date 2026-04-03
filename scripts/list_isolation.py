#!/usr/bin/env python3
"""
查看Agent数据隔离配置
"""

import json
import sys
from pathlib import Path

def get_config_path():
    """获取配置文件路径"""
    paths = [
        Path.home() / ".openclaw" / "openclaw.json",
        Path.home() / "AppData" / "Roaming" / "zhengfeiClaw" / "openclaw" / "state" / "openclaw.json",
    ]
    
    for path in paths:
        if path.exists():
            return path
    
    return None

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        return None

def get_isolation_type_name(isolation_type):
    """获取隔离类型的中文名称"""
    type_names = {
        "conversation_memory": "机器人对话记忆",
        "user_preferences": "用户偏好设置",
        "task_records": "任务记录、执行日志、任务状态",
        "session_context": "会话上下文、历史对话消息",
        "user_profile": "用户画像、私有业务数据",
        "temporary_state": "临时会话状态、缓存数据",
        "all": "所有数据类型"
    }
    
    return type_names.get(isolation_type, isolation_type)

def list_isolation():
    """列出数据隔离配置"""
    config_path = get_config_path()
    if not config_path:
        print("❌ 找不到OpenClaw配置文件")
        return 1
    
    config = load_config(config_path)
    if config is None:
        return 1
    
    agents = config.get("agents", {}).get("list", [])
    if not agents:
        print("📋 没有配置Agent")
        return 0
    
    print("📋 Agent数据隔离配置")
    print("=" * 80)
    
    # 显示session配置
    session = config.get("session", {})
    dm_scope = session.get("dmScope", "未设置")
    
    print(f"📊 全局会话配置")
    print(f"  session.dmScope: {dm_scope}")
    
    dm_scope_descriptions = {
        "main": "主会话 - 所有渠道共享一个会话",
        "per-peer": "按用户 - 每个用户独立会话",
        "per-channel-peer": "按渠道+用户 - 每个渠道的每个用户独立会话",
        "per-account-channel-peer": "按账户+渠道+用户 - 每个账户每个渠道每个用户独立会话"
    }
    
    if dm_scope in dm_scope_descriptions:
        print(f"    描述: {dm_scope_descriptions[dm_scope]}")
    
    print("\n🤖 Agent隔离配置")
    print("-" * 40)
    
    isolation_stats = {
        "full_isolation": 0,      # 完全隔离
        "partial_share": 0,       # 部分共享
        "full_share": 0,          # 完全共享
        "not_set": 0              # 未设置
    }
    
    for agent in agents:
        agent_id = agent.get("id", "未知")
        agent_name = agent.get("name", "未命名")
        
        print(f"\n🔸 {agent_name} ({agent_id})")
        
        # 检查隔离配置
        if "dataIsolation" not in agent:
            print("  隔离配置: 未设置")
            isolation_stats["not_set"] += 1
            continue
        
        isolation = agent["dataIsolation"]
        enabled = isolation.get("enabled", False)
        shared_types = isolation.get("sharedTypes", [])
        
        if not enabled:
            # 完全隔离
            print("  隔离级别: 完全隔离（默认）")
            print("  描述: 机器人完全独立运行，不共享任何数据")
            isolation_stats["full_isolation"] += 1
            
        elif "all" in shared_types:
            # 完全共享
            print("  隔离级别: 完全共享")
            print("  描述: 所有数据类型完全共享")
            isolation_stats["full_share"] += 1
            
        else:
            # 部分共享
            print("  隔离级别: 部分共享")
            print("  描述: 只共享指定的数据类型")
            isolation_stats["partial_share"] += 1
            
            if shared_types:
                print("  共享的数据类型:")
                for st in shared_types:
                    type_name = get_isolation_type_name(st)
                    print(f"    - {type_name}")
            else:
                print("  共享的数据类型: 无")
        
        # 显示共享Skill配置
        shared_skills = agent.get("sharedSkills", "未设置")
        shared_permissions = agent.get("sharedPermissions", "未设置")
        
        print(f"  Skill共享: {shared_skills}")
        print(f"  权限共享: {shared_permissions}")
    
    # 显示统计信息
    print("\n📊 隔离配置统计")
    print("-" * 40)
    
    total_agents = len(agents)
    print(f"总Agent数量: {total_agents}")
    print(f"完全隔离: {isolation_stats['full_isolation']}")
    print(f"部分共享: {isolation_stats['partial_share']}")
    print(f"完全共享: {isolation_stats['full_share']}")
    print(f"未设置: {isolation_stats['not_set']}")
    
    # 显示隔离建议
    print("\n💡 隔离配置建议")
    print("-" * 40)
    
    if dm_scope == "per-account-channel-peer":
        print("✅ 当前session.dmScope配置为'per-account-channel-peer'，适合多机器人场景")
        print("   每个飞书机器人账户、每个渠道、每个用户都有独立的会话")
    elif dm_scope == "per-channel-peer":
        print("⚠️  session.dmScope配置为'per-channel-peer'，部分共享会话")
        print("   同一渠道的不同机器人账户会共享用户会话")
    elif dm_scope == "per-peer":
        print("⚠️  session.dmScope配置为'per-peer'，较高程度的共享")
        print("   所有渠道的同一用户会共享会话")
    elif dm_scope == "main":
        print("❌ session.dmScope配置为'main'，完全共享会话")
        print("   所有用户、所有渠道、所有机器人共享一个会话，不适合多机器人场景")
    
    # 检查配置一致性
    print("\n🔍 配置一致性检查")
    print("-" * 40)
    
    # 检查是否有Agent配置了部分共享但dmScope不允许
    if dm_scope == "main":
        partial_share_agents = []
        for agent in agents:
            isolation = agent.get("dataIsolation", {})
            if isolation.get("enabled", False) and "all" not in isolation.get("sharedTypes", []):
                partial_share_agents.append(agent.get("id"))
        
        if partial_share_agents:
            print(f"⚠️  以下Agent配置了部分共享，但session.dmScope='main'可能无法正确隔离:")
            for agent_id in partial_share_agents:
                print(f"    - {agent_id}")
    
    print("\n" + "=" * 80)
    print(f"配置文件: {config_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(list_isolation())