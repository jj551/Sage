import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SessionManager:
    def __init__(self, db_path: str = 'sessions.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                last_accessed_at TEXT,
                data_source_uri TEXT,
                message_history TEXT,
                agent_state TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create_session(self, session_id: str, data_source_uri: str = "") -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO sessions (session_id, created_at, last_accessed_at, data_source_uri, message_history, agent_state) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, now, now, data_source_uri, json.dumps([]), json.dumps({}))
        )
        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            session_data = {
                "session_id": row[0],
                "created_at": row[1],
                "last_accessed_at": row[2],
                "data_source_uri": row[3],
                "message_history": json.loads(row[4]),
                "agent_state": json.loads(row[5])
            }
            self._update_last_accessed(session_id)
            return session_data
        return None

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        set_clauses = []
        params = []
        for key, value in updates.items():
            if key in ["message_history", "agent_state"]:
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            params.append(value)
        
        params.append(session_id)
        query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE session_id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        self._update_last_accessed(session_id)

    def _update_last_accessed(self, session_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("UPDATE sessions SET last_accessed_at = ? WHERE session_id = ?", (now, session_id))
        conn.commit()
        conn.close()

    def delete_session(self, session_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_context_for_llm(self, session_id: str) -> str:
        session_data = self.get_session(session_id)
        if session_data:
            history = session_data.get("message_history", [])
            # Simple concatenation for now, can be refined with more sophisticated prompt engineering
            context_messages = [f"User: {msg['user']}\nAgent: {msg['agent']}" for msg in history if 'user' in msg and 'agent' in msg]
            agent_state = session_data.get("agent_state", {})
            
            context = "\n".join(context_messages)
            if agent_state:
                context += f"\nCurrent Agent State: {json.dumps(agent_state, indent=2)}"
            return context
        return ""

if __name__ == '__main__':
    sm = SessionManager()
    session_id = "test_session_123"

    # Create a new session
    sm.create_session(session_id, data_source_uri="file://sales.csv")
    print(f"Created session: {sm.get_session(session_id)}")

    # Update message history
    sm.update_session(session_id, {
        "message_history": [{"user": "Hello", "agent": "Hi there!"}, {"user": "Analyze sales", "agent": "Sure, loading data."}]
    })
    print(f"Updated session: {sm.get_session(session_id)}")

    # Get context for LLM
    print("\nContext for LLM:")
    print(sm.get_context_for_llm(session_id))

    # Delete session
    sm.delete_session(session_id)
    print(f"Session {session_id} deleted.")
    print(f"Session after deletion: {sm.get_session(session_id)}")
