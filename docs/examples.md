# Code Examples

Practical examples and use cases for BPSR Labs.

## Basic Examples

### Combat Packet Analysis

```python
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader

# Load and decode a capture file
with open('data/captures/combat.bin', 'rb') as f:
    data = f.read()

reader = FrameReader()
decoder = CombatDecoder()

for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        print(f"Method: 0x{frame.method_id:08x}, Type: {record.message_type}")
        print(f"Data: {record.to_dict()}")
```

### Trading Center Analysis

```python
from bpsr_labs.packet_decoder.decoder.trading_center_decode import extract_listing_blocks, consolidate
from bpsr_labs.packet_decoder.decoder.item_catalog import load_item_mapping

# Load and decode trading center data
with open('data/captures/trading.bin', 'rb') as f:
    data = f.read()

# Extract listings
listings = extract_listing_blocks(data)

# Load item mappings
item_mapping = load_item_mapping()

# Consolidate with item names
consolidated = consolidate(listings, resolver=lambda item_id: item_mapping.get(item_id))

for listing in consolidated:
    print(f"Item: {listing.get('item_name', 'Unknown')} - Price: {listing['price_luno']} Luno")
```

### DPS Analysis

```python
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer
import json

# Process decoded records
reducer = CombatReducer()

# Load decoded combat data
with open('data/captures/decoded.jsonl') as f:
    for line in f:
        record = json.loads(line)
        reducer.process_record(record)

# Generate summary
summary = reducer.summary()

print(f"Total Damage: {summary['total_damage']}")
print(f"DPS: {summary['dps']:.2f}")
print(f"Skills: {len(summary['skills'])}")
print(f"Targets: {len(summary['targets'])}")
```

## Advanced Examples

### Custom Decoder Configuration

```python
from bpsr_labs.packet_decoder.decoder.combat_decode_v2 import CombatDecoderV2
from bpsr_labs.packet_decoder.decoder.trading_center_decode_v2 import TradingDecoderV2

# Configure V2 decoders with custom settings
combat_decoder = CombatDecoderV2(
    fallback_to_v1=True,  # Enable V1 fallback
    verbose=True          # Enable debug output
)

trading_decoder = TradingDecoderV2(
    resolve_item_names=True,
    custom_item_mapping="data/custom_mapping.json"
)

# Use in processing pipeline
for frame in reader.iter_notify_frames(data):
    if frame.method_id == 0x2e:  # Combat frame
        record = combat_decoder.decode(frame)
    elif frame.method_id == 0x42:  # Trading frame
        record = trading_decoder.decode(frame)
```

### Data Analysis with Pandas

```python
import pandas as pd
import matplotlib.pyplot as plt
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader

# Load and decode combat data
reader = FrameReader()
decoder = CombatDecoder()
records = []

with open('data/captures/combat.bin', 'rb') as f:
    data = f.read()

for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        records.append(record.to_dict())

# Convert to DataFrame
df = pd.DataFrame(records)

# Analyze damage over time
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
damage_by_time = df.groupby(df['timestamp'].dt.floor('1s'))['damage'].sum()

# Plot damage over time
plt.figure(figsize=(12, 6))
damage_by_time.plot(kind='line', title='Damage Over Time')
plt.xlabel('Time')
plt.ylabel('Damage')
plt.grid(True)
plt.show()

# Skill usage analysis
skill_usage = df.groupby('skill_id').agg({
    'damage': ['sum', 'count', 'mean'],
    'crit': 'sum'
}).round(2)

print("Skill Analysis:")
print(skill_usage)
```

### Building Analysis Pipelines

```python
from pathlib import Path
import json
from typing import Dict, List, Any
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer

class CombatAnalysisPipeline:
    """Complete combat analysis pipeline."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        
    def process_file(self, input_file: Path) -> Dict[str, Any]:
        """Process a single combat capture file."""
        print(f"Processing {input_file.name}...")
        
        # Decode packets
        records = self._decode_packets(input_file)
        
        # Calculate DPS
        dps_summary = self._calculate_dps(records)
        
        # Save results
        self._save_results(input_file.stem, records, dps_summary)
        
        return dps_summary
    
    def _decode_packets(self, input_file: Path) -> List[Dict[str, Any]]:
        """Decode combat packets from capture file."""
        reader = FrameReader()
        decoder = CombatDecoder()
        records = []
        
        with open(input_file, 'rb') as f:
            data = f.read()
        
        for frame in reader.iter_notify_frames(data):
            record = decoder.decode(frame)
            if record:
                records.append(record.to_dict())
        
        return records
    
    def _calculate_dps(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate DPS metrics from decoded records."""
        reducer = CombatReducer()
        
        for record in records:
            reducer.process_record(record)
        
        return reducer.summary()
    
    def _save_results(self, filename: str, records: List[Dict[str, Any]], dps_summary: Dict[str, Any]):
        """Save analysis results to files."""
        # Save raw records
        records_file = self.output_dir / f"{filename}_records.jsonl"
        with open(records_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
        
        # Save DPS summary
        dps_file = self.output_dir / f"{filename}_dps.json"
        with open(dps_file, 'w') as f:
            json.dump(dps_summary, f, indent=2)
        
        print(f"Saved results to {records_file} and {dps_file}")

# Usage
pipeline = CombatAnalysisPipeline(Path("analysis_output"))

for capture_file in Path("data/captures").glob("*combat*.bin"):
    result = pipeline.process_file(capture_file)
    print(f"DPS: {result['dps']:.1f}, Duration: {result['active_duration_s']:.1f}s")
```

## Batch Processing

### Process Multiple Files

```python
from pathlib import Path
import subprocess
import json

def process_all_captures(input_dir: Path, output_dir: Path):
    """Process all capture files in a directory."""
    output_dir.mkdir(exist_ok=True)
    
    for capture_file in input_dir.glob("*.bin"):
        print(f"Processing {capture_file.name}...")
        
        # Determine file type and process accordingly
        if "combat" in capture_file.name.lower():
            process_combat_file(capture_file, output_dir)
        elif "trading" in capture_file.name.lower():
            process_trading_file(capture_file, output_dir)

def process_combat_file(input_file: Path, output_dir: Path):
    """Process a combat capture file."""
    jsonl_file = output_dir / f"{input_file.stem}.jsonl"
    dps_file = output_dir / f"{input_file.stem}_dps.json"
    
    # Decode combat packets
    subprocess.run([
        "poetry", "run", "bpsr-labs", "decode",
        str(input_file), str(jsonl_file)
    ], check=True)
    
    # Calculate DPS
    subprocess.run([
        "poetry", "run", "bpsr-labs", "dps",
        str(jsonl_file), str(dps_file)
    ], check=True)
    
    # Load and display results
    with open(dps_file) as f:
        dps_data = json.load(f)
    
    print(f"  DPS: {dps_data['dps']:.1f}")
    print(f"  Total Damage: {dps_data['total_damage']:,}")

def process_trading_file(input_file: Path, output_dir: Path):
    """Process a trading center capture file."""
    json_file = output_dir / f"{input_file.stem}_listings.json"
    
    # Decode trading center packets
    subprocess.run([
        "poetry", "run", "bpsr-labs", "trade-decode",
        str(input_file), str(json_file)
    ], check=True)
    
    # Load and display results
    with open(json_file) as f:
        listings = json.load(f)
    
    print(f"  Found {len(listings)} listings")
    if listings:
        avg_price = sum(l.get('price_luno', 0) for l in listings) / len(listings)
        print(f"  Average price: {avg_price:.0f} Luno")

# Run batch processing
process_all_captures(Path("data/captures"), Path("analysis_output"))
```

### Parallel Processing

```python
import concurrent.futures
from pathlib import Path
import subprocess

def process_file_parallel(input_file: Path, output_dir: Path):
    """Process a single file (for parallel execution)."""
    try:
        if "combat" in input_file.name.lower():
            # Process combat file
            jsonl_file = output_dir / f"{input_file.stem}.jsonl"
            dps_file = output_dir / f"{input_file.stem}_dps.json"
            
            subprocess.run([
                "poetry", "run", "bpsr-labs", "decode",
                str(input_file), str(jsonl_file)
            ], check=True)
            
            subprocess.run([
                "poetry", "run", "bpsr-labs", "dps",
                str(jsonl_file), str(dps_file)
            ], check=True)
            
            return f"✓ {input_file.name} - Combat processed"
            
        elif "trading" in input_file.name.lower():
            # Process trading file
            json_file = output_dir / f"{input_file.stem}_listings.json"
            
            subprocess.run([
                "poetry", "run", "bpsr-labs", "trade-decode",
                str(input_file), str(json_file)
            ], check=True)
            
            return f"✓ {input_file.name} - Trading processed"
            
    except subprocess.CalledProcessError as e:
        return f"✗ {input_file.name} - Error: {e}"

def process_all_parallel(input_dir: Path, output_dir: Path, max_workers: int = 4):
    """Process all files in parallel."""
    output_dir.mkdir(exist_ok=True)
    
    capture_files = list(input_dir.glob("*.bin"))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_file_parallel, file, output_dir)
            for file in capture_files
        ]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(result)

# Run parallel processing
process_all_parallel(Path("data/captures"), Path("analysis_output"), max_workers=4)
```

## Integration Examples

### Jupyter Notebook Integration

```python
# In a Jupyter notebook cell
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader

# Load combat data
def load_combat_data(file_path):
    reader = FrameReader()
    decoder = CombatDecoder()
    records = []
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    for frame in reader.iter_notify_frames(data):
        record = decoder.decode(frame)
        if record:
            records.append(record.to_dict())
    
    return pd.DataFrame(records)

# Load and analyze
df = load_combat_data('data/captures/combat_session_1.bin')

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Damage over time
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
damage_by_time = df.groupby(df['timestamp'].dt.floor('5s'))['damage'].sum()
damage_by_time.plot(ax=axes[0,0], title='Damage Over Time (5s intervals)')

# Skill usage
skill_usage = df['skill_id'].value_counts().head(10)
skill_usage.plot(kind='bar', ax=axes[0,1], title='Top 10 Skills by Usage')

# Critical hit rate
crit_rate = df.groupby('skill_id')['crit'].mean().sort_values(ascending=False).head(10)
crit_rate.plot(kind='bar', ax=axes[1,0], title='Critical Hit Rate by Skill')

# Damage distribution
df['damage'].hist(bins=50, ax=axes[1,1], title='Damage Distribution')

plt.tight_layout()
plt.show()
```

### Web Dashboard Integration

```python
# Flask web app example
from flask import Flask, render_template, jsonify, request
import subprocess
import json
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/process-combat', methods=['POST'])
def process_combat():
    """Process combat file and return DPS data."""
    file_path = request.json['file_path']
    
    # Decode packets
    jsonl_file = f"{file_path}.jsonl"
    subprocess.run([
        "poetry", "run", "bpsr-labs", "decode",
        file_path, jsonl_file
    ], check=True)
    
    # Calculate DPS
    dps_file = f"{file_path}_dps.json"
    subprocess.run([
        "poetry", "run", "bpsr-labs", "dps",
        jsonl_file, dps_file
    ], check=True)
    
    # Load results
    with open(dps_file) as f:
        dps_data = json.load(f)
    
    return jsonify(dps_data)

@app.route('/api/process-trading', methods=['POST'])
def process_trading():
    """Process trading center file and return listings."""
    file_path = request.json['file_path']
    
    # Decode trading center
    json_file = f"{file_path}_listings.json"
    subprocess.run([
        "poetry", "run", "bpsr-labs", "trade-decode",
        file_path, json_file
    ], check=True)
    
    # Load results
    with open(json_file) as f:
        listings = json.load(f)
    
    return jsonify(listings)

if __name__ == '__main__':
    app.run(debug=True)
```

### Database Storage

```python
import sqlite3
import json
from pathlib import Path
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader

class CombatDatabase:
    """Store combat analysis results in SQLite database."""
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS combat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                total_damage INTEGER,
                dps REAL,
                duration_s REAL,
                hits INTEGER,
                crits INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS skill_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                skill_id TEXT,
                damage INTEGER,
                hits INTEGER,
                crits INTEGER,
                FOREIGN KEY (session_id) REFERENCES combat_sessions (id)
            )
        ''')
        
        self.conn.commit()
    
    def store_combat_analysis(self, filename: str, capture_file: Path):
        """Store combat analysis results."""
        # Process the file
        reader = FrameReader()
        decoder = CombatDecoder()
        records = []
        
        with open(capture_file, 'rb') as f:
            data = f.read()
        
        for frame in reader.iter_notify_frames(data):
            record = decoder.decode(frame)
            if record:
                records.append(record.to_dict())
        
        # Calculate summary
        from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer
        reducer = CombatReducer()
        for record in records:
            reducer.process_record(record)
        summary = reducer.summary()
        
        # Store session data
        cursor = self.conn.execute('''
            INSERT OR REPLACE INTO combat_sessions 
            (filename, total_damage, dps, duration_s, hits, crits)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            summary['total_damage'],
            summary['dps'],
            summary['active_duration_s'],
            summary['hits'],
            summary['crits']
        ))
        
        session_id = cursor.lastrowid
        
        # Store skill usage data
        for skill_id, skill_data in summary['skills'].items():
            self.conn.execute('''
                INSERT INTO skill_usage 
                (session_id, skill_id, damage, hits, crits)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                skill_id,
                skill_data['damage'],
                skill_data['hits'],
                skill_data['crits']
            ))
        
        self.conn.commit()
        return session_id
    
    def get_session_summary(self, session_id: int):
        """Get summary for a specific session."""
        cursor = self.conn.execute('''
            SELECT * FROM combat_sessions WHERE id = ?
        ''', (session_id,))
        
        return cursor.fetchone()
    
    def get_top_skills(self, limit: int = 10):
        """Get most used skills across all sessions."""
        cursor = self.conn.execute('''
            SELECT skill_id, SUM(damage) as total_damage, SUM(hits) as total_hits
            FROM skill_usage
            GROUP BY skill_id
            ORDER BY total_damage DESC
            LIMIT ?
        ''', (limit,))
        
        return cursor.fetchall()

# Usage
db = CombatDatabase('combat_analysis.db')

# Store analysis for all combat files
for combat_file in Path('data/captures').glob('*combat*.bin'):
    session_id = db.store_combat_analysis(combat_file.name, combat_file)
    print(f"Stored analysis for {combat_file.name} (session {session_id})")

# Query results
print("Top skills by damage:")
for skill_id, total_damage, total_hits in db.get_top_skills(5):
    print(f"  {skill_id}: {total_damage:,} damage, {total_hits} hits")
```

## Real-world Use Cases

### DPS Optimization Analysis

```python
def analyze_dps_optimization(capture_files: List[Path]):
    """Analyze multiple combat sessions to find optimization opportunities."""
    results = []
    
    for file_path in capture_files:
        # Process each file
        reader = FrameReader()
        decoder = CombatDecoder()
        records = []
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        for frame in reader.iter_notify_frames(data):
            record = decoder.decode(frame)
            if record:
                records.append(record.to_dict())
        
        # Calculate DPS
        reducer = CombatReducer()
        for record in records:
            reducer.process_record(record)
        summary = reducer.summary()
        
        results.append({
            'filename': file_path.name,
            'dps': summary['dps'],
            'duration': summary['active_duration_s'],
            'total_damage': summary['total_damage'],
            'skills': summary['skills']
        })
    
    # Find optimization opportunities
    best_session = max(results, key=lambda x: x['dps'])
    worst_session = min(results, key=lambda x: x['dps'])
    
    print(f"Best DPS: {best_session['dps']:.1f} ({best_session['filename']})")
    print(f"Worst DPS: {worst_session['dps']:.1f} ({worst_session['filename']})")
    
    # Analyze skill usage differences
    best_skills = set(best_session['skills'].keys())
    worst_skills = set(worst_session['skills'].keys())
    
    print(f"Skills only in best session: {best_skills - worst_skills}")
    print(f"Skills only in worst session: {worst_skills - best_skills}")
    
    return results
```

### Trading Center Market Analysis

```python
def analyze_trading_market(capture_files: List[Path]):
    """Analyze trading center data for market insights."""
    all_listings = []
    
    for file_path in capture_files:
        # Decode trading center data
        listings = extract_listing_blocks(open(file_path, 'rb').read())
        
        # Load item mappings
        item_mapping = load_item_mapping()
        
        # Consolidate with item names
        consolidated = consolidate(listings, resolver=lambda item_id: item_mapping.get(item_id))
        all_listings.extend(consolidated)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_listings)
    
    if df.empty:
        print("No trading data found")
        return
    
    # Market analysis
    print(f"Total listings analyzed: {len(df)}")
    print(f"Unique items: {df['item_id'].nunique()}")
    print(f"Average price: {df['price_luno'].mean():.0f} Luno")
    print(f"Price range: {df['price_luno'].min():.0f} - {df['price_luno'].max():.0f} Luno")
    
    # Top items by volume
    top_items = df.groupby('item_id').agg({
        'quantity': 'sum',
        'price_luno': 'mean'
    }).sort_values('quantity', ascending=False).head(10)
    
    print("\nTop 10 items by volume:")
    for item_id, row in top_items.iterrows():
        item_name = item_mapping.get(item_id, f"Item_{item_id}")
        print(f"  {item_name}: {row['quantity']} units @ {row['price_luno']:.0f} Luno avg")
    
    # Price analysis
    price_stats = df.groupby('item_id')['price_luno'].agg(['count', 'mean', 'std', 'min', 'max'])
    high_variance_items = price_stats[price_stats['std'] > price_stats['mean'] * 0.5]
    
    print(f"\nItems with high price variance ({len(high_variance_items)} items):")
    for item_id, row in high_variance_items.head(5).iterrows():
        item_name = item_mapping.get(item_id, f"Item_{item_id}")
        print(f"  {item_name}: {row['mean']:.0f} ± {row['std']:.0f} Luno")
    
    return df
```
