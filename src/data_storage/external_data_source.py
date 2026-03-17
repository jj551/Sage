from typing import Optional, Dict, Any
from urllib.parse import urlparse
import pandas as pd

class ExternalDataSource:
    def __init__(self):
        self.connections: Dict[str, Any] = {}
    
    def connect(self, source_uri: str, **kwargs) -> None:
        parsed = urlparse(source_uri)
        
        if parsed.scheme in ['file', '']:
            print(f"ExternalDataSource: File connection (read-only)")
        elif parsed.scheme == 'db':
            print(f"ExternalDataSource: Database connection (read-only)")
        elif parsed.scheme == 's3':
            print(f"ExternalDataSource: S3 connection (read-only)")
        else:
            raise ValueError(f"Unsupported scheme: {parsed.scheme}")
        
        self.connections[source_uri] = {"connected": True, **kwargs}
    
    def is_connected(self, source_uri: str) -> bool:
        return source_uri in self.connections and self.connections[source_uri]["connected"]
    
    def get_metadata(self, source_uri: str) -> Optional[Dict[str, Any]]:
        if not self.is_connected(source_uri):
            return None
        
        parsed = urlparse(source_uri)
        metadata = {
            "uri": source_uri,
            "scheme": parsed.scheme,
            "read_only": True,
            "last_verified": None
        }
        return metadata
    
    def disconnect(self, source_uri: str) -> None:
        if source_uri in self.connections:
            del self.connections[source_uri]
    
    def disconnect_all(self) -> None:
        self.connections.clear()

if __name__ == '__main__':
    eds = ExternalDataSource()
    
    print("--- Testing ExternalDataSource ---")
    test_uri = "file:///tmp/test.csv"
    eds.connect(test_uri)
    print(f"Connected to {test_uri}: {eds.is_connected(test_uri)}")
    
    metadata = eds.get_metadata(test_uri)
    print(f"Metadata: {metadata}")
    
    eds.disconnect(test_uri)
    print(f"Disconnected from {test_uri}: {eds.is_connected(test_uri)}")
