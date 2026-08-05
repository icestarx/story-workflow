# registry.json 字段说明

registry.json 是 Canon 的检索索引，不是完整小说数据库。字段保持小而稳定，细节继续写在对应 Markdown 中。

    {
      "schema_version": 1,
      "canon_version": "0.1.0",
      "entities": [
        {"id": "char.hero", "type": "character", "name": "主角", "status": "confirmed", "source_file": "01-canon/characters/hero.md"}
      ],
      "facts": [
        {"id": "world.cost", "statement": "使用术式会消耗寿元", "status": "confirmed", "source_steps": [34], "visibility": "public", "source_file": "01-canon/world.md"}
      ],
      "foreshadows": [
        {"id": "foreshadow.seal", "setup_chapter": 3, "status": "open", "target_window": "45-60", "responsible_chapter": 52}
      ],
      "changes": [
        {"version": "0.2.0", "date": "YYYY-MM-DD", "reason": "批准新角色状态", "affected_ids": ["char.hero"], "approved_by": "user"}
      ]
    }

常用状态：candidate、confirmed、tbd、deprecated；伏笔可另用 open、advanced、resolved、retired。visibility 用 public、character-limited 或 author-only 表示叙事可见范围，但角色知识仍需在角色/状态文档中登记。

ID 在 entities、facts、foreshadows 中必须全局唯一。source_file 必须是项目目录内的相对路径。
