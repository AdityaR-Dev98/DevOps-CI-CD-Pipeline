try:
    import json
    import pandas as pd
    import os
    
    def load_json_data(filepath):
        """Load JSON file from given path"""
        with open(filepath, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data

except FileNotFoundError:
    print('File not found, using default fallback.')