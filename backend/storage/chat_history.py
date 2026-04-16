from typing import List, Dict, Any
from collections import defaultdict

class ChatMemory:
    """
    A simple in-memory session-based chat history storage.
    In production, this would be replaced with Redis or a database.
    """
    def __init__(self, max_history: int = 20, storage_path: str = "logs/chat_history.json"):
        self.history: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.metadata: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.max_history = max_history
        self.storage_path = storage_path
        self._load_from_disk()

    def _load_from_disk(self):
        import os, json
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.history.update(data.get("history", {}))
                    self.metadata.update(data.get("metadata", {}))
            except Exception as e:
                logger.error(f"Failed to load history: {e}")

    def _save_to_disk(self):
        import os, json
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w") as f:
                json.dump({
                    "history": self.history,
                    "metadata": self.metadata
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add_message(self, session_id: str, role: str, content: str):
        """Adds a message to the session history and updates metadata if new."""
        # Set default title if this is the first user message
        if session_id not in self.metadata or "title" not in self.metadata[session_id]:
            if role == "user":
                # Use first 30 chars of first user message as title
                title = content[:30] + ("..." if len(content) > 30 else "")
                self.metadata[session_id]["title"] = title
                self.metadata[session_id]["created_at"] = content # Placeholder for timestamp logic or just tracking

        self.history[session_id].append({"role": role, "content": content})
        # Keep history within limits
        if len(self.history[session_id]) > self.max_history:
            self.history[session_id] = self.history[session_id][-self.max_history:]
        
        self._save_to_disk()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves history for a session."""
        return self.history.get(session_id, [])

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Lists all stored session IDs and their metadata."""
        return [
            {"session_id": sid, "title": meta.get("title", "Untitled Session")}
            for sid, meta in self.metadata.items()
        ]

    def delete_session(self, session_id: str):
        """Removes a session and its metadata permanently."""
        print(f"DEBUG: Deleting session {session_id} from disk...")
        if session_id in self.history:
            del self.history[session_id]
        if session_id in self.metadata:
            del self.metadata[session_id]
        self._save_to_disk()

    def format_for_prompt(self, session_id: str) -> str:
        """Formats the history into a string for LLM context."""
        messages = self.get_history(session_id)
        if not messages:
            return ""
        
        formatted = ""
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        return formatted

# Global singleton for easy access across agents
chat_memory = ChatMemory()
