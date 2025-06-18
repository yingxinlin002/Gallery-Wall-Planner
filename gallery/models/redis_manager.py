import redis
import json
import uuid
from datetime import datetime, timedelta

class RedisSessionManager:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )
        self.session_ttl = timedelta(days=1)  # 24 hour expiration
        
    def create_guest_session(self, initial_data=None):
        """Create a new guest session"""
        session_id = f"guest:{uuid.uuid4()}"
        session_data = {
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'data': initial_data or {}
        }
        self.redis.setex(
            session_id,
            self.session_ttl,
            json.dumps(session_data))
        print(f"[REDIS] Created guest session: {session_id}")
        return session_id
        
    def get_session(self, session_id):
        """Get session data if it exists"""
        if not session_id or not session_id.startswith('guest:'):
            return None
            
        data = self.redis.get(session_id)
        return json.loads(data) if data else None
        
    def update_session(self, session_id, data):
        """Update session data"""
        if not session_id or not session_id.startswith('guest:'):
            return False
            
        session_data = {
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'data': data
        }
        print(f"[REDIS] Updated session: {session_id} with data keys: {list(data.keys())}")
        return self.redis.setex(
            session_id,
            self.session_ttl,
            json.dumps(session_data))
            
    def delete_session(self, session_id):
        """Delete a session"""
        if session_id and session_id.startswith('guest:'):
            self.redis.delete(session_id)