"""agent_matrix.py

    Simple SQLite storage implementation for agent cores, maintaining exact structure.

    @LeoBorcherding
    12/10/2024
"""

import sqlite3
import json
from typing import Optional, Dict, Any
from pathlib import Path

class agentMatrix:
    """Storage implementation for agent cores using SQLite."""
    def __init__(self, db_path: str = "agent_matrix.db"):
        """Initialize the agent matrix storage."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with the agent_cores table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_cores (
                    agent_id TEXT,
                    core_data TEXT,
                    save_date TEXT,
                    uid TEXT UNIQUE,
                    version INTEGER,
                    PRIMARY KEY (agent_id, uid)
                )
            """)

    def upsert(self, documents: list, ids: list, metadatas: list = None) -> None:
        """Store agent core(s) in matrix."""
        with sqlite3.connect(self.db_path) as conn:
            for idx, (doc, id_) in enumerate(zip(documents, ids)):
                metadata = metadatas[idx] if metadatas else {'save_date': None}
                conn.execute(
                    "INSERT OR REPLACE INTO agent_cores (agent_id, core_data, save_date) VALUES (?, ?, ?)",
                    (id_, doc, metadata.get('save_date'))
                )

    def get(self, ids: Optional[list] = None) -> Dict:
        """Retrieve agent core(s) from matrix."""
        with sqlite3.connect(self.db_path) as conn:
            if ids:
                placeholders = ','.join('?' * len(ids))
                query = f"SELECT agent_id, core_data, save_date FROM agent_cores WHERE agent_id IN ({placeholders})"
                results = conn.execute(query, ids).fetchall()
            else:
                results = conn.execute("SELECT agent_id, core_data, save_date FROM agent_cores").fetchall()

            return {
                "ids": [r[0] for r in results],
                "documents": [r[1] for r in results],
                "metadatas": [{"agent_id": r[0], "save_date": r[2]} for r in results]
            }

    def delete(self, ids: list) -> None:
        """Remove agent core(s) from matrix."""
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ','.join('?' * len(ids))
            conn.execute(f"DELETE FROM agent_cores WHERE agent_id IN ({placeholders})", ids)