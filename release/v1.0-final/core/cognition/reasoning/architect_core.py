import os
import ast
import traceback

# 🏗️ O.M.E.G.A. ARCHITECT_CORE: SELF_REPAIR_ENGINE_V1
# This core handles automated code restoration for JARVIS.

class CodeArchitect:
    def __init__(self):
        self.common_fixes = [
            self._fix_missing_colon,
            self._fix_indentation,
            self._fix_unclosed_quotes,
            self._fix_missing_brackets
        ]

    async def repair(self, file_path, error_context):
        print(f"[ARCHITECT] Analyzing instability in {file_path}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        original_code = "".join(lines)
        repaired_code = original_code

        # 1. Try common rule-based fixes
        for fix in self.common_fixes:
            repaired_code = fix(repaired_code, error_context)

        # 2. Validate repair
        try:
            compile(repaired_code, file_path, "exec")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(repaired_code)
            print(f"[ARCHITECT] [SUCCESS] Restored {os.path.basename(file_path)} to operational state.")
            return True
        except Exception as e:
            print(f"[ARCHITECT] [FAIL] Heuristic repair failed for {os.path.basename(file_path)}: {str(e)}")
            return False

    def _fix_missing_colon(self, code, error_context):
        """Fixes missing colons at the end of control statements."""
        msg = error_context.get("message", "").lower()
        if "expected ':'" not in msg:
            return code
            
        lineno = error_context.get("lineno")
        lines = code.splitlines()
        
        # If we have a line number, target it specifically
        if lineno and lineno <= len(lines):
            idx = lineno - 1
            line = lines[idx]
            stripped = line.strip()
            # If the error is on this line, it might be the previous line that needs the colon
            # or this line itself.
            if any(stripped.startswith(k) for k in ["if ", "elif ", "else", "for ", "while ", "def ", "class "]) and not stripped.endswith(":"):
                print(f"[ARCHITECT] Appending missing colon to line {lineno}")
                lines[idx] = line + ":"
            elif idx > 0:
                prev_line = lines[idx-1]
                prev_stripped = prev_line.strip()
                if any(prev_stripped.startswith(k) for k in ["if ", "elif ", "else", "for ", "while ", "def ", "class "]) and not prev_stripped.endswith(":"):
                    print(f"[ARCHITECT] Appending missing colon to previous line {lineno-1}")
                    lines[idx-1] = prev_line + ":"
        
        return "\n".join(lines)

    def _fix_indentation(self, code, error_context):
        """Basic indentation fix - targets 'expected an indented block'."""
        msg = error_context.get("message", "").lower()
        if "expected an indented block" not in msg:
            return code
            
        lineno = error_context.get("lineno")
        lines = code.splitlines()
        
        if lineno and lineno <= len(lines):
            idx = lineno - 1
            line = lines[idx]
            # Simple fix: add 4 spaces if it looks like it needs it
            if not line.startswith(" ") and not line.startswith("\t") and idx > 0:
                prev_line = lines[idx-1]
                if prev_line.strip().endswith(":"):
                    indent = ""
                    for char in prev_line:
                        if char in [" ", "\t"]: indent += char
                        else: break
                    print(f"[ARCHITECT] Fixing indentation at line {lineno}")
                    lines[idx] = indent + "    " + line
                    
        return "\n".join(lines)

    def _fix_unclosed_quotes(self, code, error_context):
        """Fixes simple unclosed string quotes."""
        msg = error_context.get("message", "").lower()
        if "unterminated string literal" not in msg and "eof while scanning string literal" not in msg:
            return code
            
        lineno = error_context.get("lineno")
        lines = code.splitlines()
        
        if lineno and lineno <= len(lines):
            idx = lineno - 1
            line = lines[idx]
            # Count quotes in line
            single = line.count("'")
            double = line.count('"')
            
            if single % 2 != 0:
                print(f"[ARCHITECT] Closing single quote at line {lineno}")
                lines[idx] = line + "'"
            elif double % 2 != 0:
                print(f"[ARCHITECT] Closing double quote at line {lineno}")
                lines[idx] = line + '"'
                
        return "\n".join(lines)

    def _fix_missing_brackets(self, code, error_context):
        """Fixes missing closing brackets: ), ], }."""
        msg = error_context.get("message", "").lower()
        if "never closed" not in msg and "unexpected eof" not in msg:
            return code
            
        lineno = error_context.get("lineno")
        lines = code.splitlines()
        
        if lineno and lineno <= len(lines):
            idx = lineno - 1
            line = lines[idx]
            
            pairs = { '(': ')', '[': ']', '{': '}' }
            for opener, closer in pairs.items():
                if line.count(opener) > line.count(closer):
                    print(f"[ARCHITECT] Closing bracket '{closer}' at line {lineno}")
                    lines[idx] = line + closer
        
        return "\n".join(lines)

architect_core = CodeArchitect()
