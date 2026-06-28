
import os
import sys
from collections import defaultdict

class ProjectAuditor:
    """[AUDIT] O.M.E.G.A. ARCHITECTURE_AUDITOR: Structural Integrity Scan."""
    
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        self.stats = {
            "total_files": 0,
            "py_files": 0,
            "js_ts_files": 0,
            "oversized_files": [],
            "imports": defaultdict(int),
            "potential_duplicates": defaultdict(list)
        }
        self.max_lines = 500 # Threshold for oversized files

    def run_audit(self):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
            
        print(f"[AUDIT] Starting Enterprise Architecture Scan in {os.path.abspath(self.root_dir)}...")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip hidden and legacy dirs
            if any(x in root for x in [".git", "node_modules", "archive", "old_versions"]):
                continue
                
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".tsx")):
                    self.process_file(os.path.join(root, file))

        self.report()

    def process_file(self, file_path):
        self.stats["total_files"] += 1
        ext = os.path.splitext(file_path)[1]
        
        if ext == ".py":
            self.stats["py_files"] += 1
        else:
            self.stats["js_ts_files"] += 1

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                line_count = len(lines)
                
                if line_count > self.max_lines:
                    self.stats["oversized_files"].append((file_path, line_count))

                # Simple import detection
                for line in lines:
                    line = line.strip()
                    if line.startswith(("import ", "from ")):
                        self.stats["imports"][line] += 1
                        
        except Exception as e:
            print(f"⚠️ [AUDIT_ERR] Could not read {file_path}: {e}")

    def report(self):
        print("\n" + "="*50)
        print("📊 O.M.E.G.A. ARCHITECTURE REPORT")
        print("="*50)
        print(f"Total Source Files: {self.stats['total_files']}")
        print(f"Python Files:      {self.stats['py_files']}")
        print(f"JS/TS Files:      {self.stats['js_ts_files']}")
        
        if self.stats["oversized_files"]:
            print(f"\n[WARNING] OVERSIZED FILES (>{self.max_lines} lines):")
            for path, count in sorted(self.stats["oversized_files"], key=lambda x: x[1], reverse=True):
                print(f"  - {path} ({count} lines)")

        print("\n[OK] Audit Complete. Use 'ruff' and 'pyright' for deep analysis.")

if __name__ == "__main__":
    auditor = ProjectAuditor()
    auditor.run_audit()
