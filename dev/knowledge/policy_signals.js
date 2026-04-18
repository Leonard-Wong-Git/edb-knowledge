window.POLICY_SIGNALS = {
  "_meta": {
    "schema": "policy_signals_v1",
    "description": "EDB Circular System → K1 Knowledge Platform 更新訊號。由 edb_scraper.py _apply_post_analysis_review() 末段靜默寫入。管理員人手決定是否更新知識庫，完成後改 status 為 reviewed。",
    "trigger_mode": "strong",
    "trigger_conditions": {
      "title_keywords": [
        "架構",
        "課程框架",
        "學習宗旨",
        "指引（YYYY）",
        "指引（20XX）"
      ],
      "ai_topics": [
        "curriculum"
      ]
    },
    "status_values": {
      "pending_review": "新訊號，待管理員確認是否處理",
      "auto_processed": "process_signals.py 已自動處理（下載、提取、Channel A 候選已加入）",
      "reviewed": "管理員人手確認完成",
      "skipped_duplicate": "source_id 已存在 source_registry，跳過",
      "download_failed": "PDF 下載失敗",
      "extract_failed": "pdftotext 提取失敗"
    },
    "created": "2026-04-17",
    "updated": "2026-04-18"
  },
  "signals": [
    {
      "signal_id": "sig_edbc002_2026",
      "circular_id": "EDBC002/2026",
      "title": "教育局通告第2/2026號 — 地理科（中一至中三）課程框架",
      "url": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26002C.pdf",
      "signal_date": "2026-04-17",
      "trigger_reason": {
        "title_keywords_matched": [
          "課程框架"
        ],
        "ai_topics_matched": [
          "curriculum"
        ],
        "accuracy_verified": true,
        "notes": "✅ 確認正確 — 地理科課程框架，屬 curriculum 政策文件"
      },
      "status": "auto_processed",
      "processed_at": "2026-04-18T07:02:23Z",
      "source_id": "edbc002_2026",
      "channel_a_candidates_added": 12,
      "notes": "Auto-processed via process_signals.py. 12 Channel A candidates added. Signal accuracy verified 2026-04-18."
    },
    {
      "signal_id": "sig_edbc003_2026",
      "circular_id": "EDBC003/2026",
      "title": "教育局通告第3/2026號 — 《價值觀教育課程架構》（2026）",
      "url": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26003C.pdf",
      "signal_date": "2026-04-17",
      "trigger_reason": {
        "title_keywords_matched": [
          "架構"
        ],
        "ai_topics_matched": [
          "curriculum"
        ],
        "accuracy_verified": true,
        "notes": "✅ 確認正確 — 價值觀教育課程架構（2026），屬 curriculum 政策文件"
      },
      "status": "auto_processed",
      "processed_at": "2026-04-18T07:02:34Z",
      "source_id": "edbc003_2026",
      "channel_a_candidates_added": 5,
      "notes": "Auto-processed via process_signals.py. 5 Channel A candidates added. Signal accuracy verified 2026-04-18."
    },
    {
      "signal_id": "sig_edbc005_2026",
      "circular_id": "EDBC005/2026",
      "title": "教育局通告第5/2026號 — 更新小學及中學教育的學習宗旨",
      "url": "https://applications.edb.gov.hk/circular/upload/EDBC/EDBC26005C.pdf",
      "signal_date": "2026-04-17",
      "trigger_reason": {
        "title_keywords_matched": [
          "學習宗旨"
        ],
        "ai_topics_matched": [
          "curriculum"
        ],
        "accuracy_verified": true,
        "notes": "✅ 確認正確 — 更新學習宗旨，屬 curriculum 核心政策文件"
      },
      "status": "auto_processed",
      "processed_at": "2026-04-18T07:02:41Z",
      "source_id": "edbc005_2026",
      "channel_a_candidates_added": 5,
      "notes": "Auto-processed via process_signals.py. 5 Channel A candidates added. Signal accuracy verified 2026-04-18."
    }
  ]
};
