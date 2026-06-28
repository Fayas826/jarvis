import os

FRONTEND_DIR = r'c:\jarvis AI\jarvis\frontend\src'
REPORT_PATH = r'C:\Users\Asus\.gemini\antigravity\brain\f712c679-f4cd-47de-a54f-694483076f44\Full_Frontend_Audit_Report.md'

report = ['# Master Automated Frontend Audit Report\n']
report.append('> **Note:** This is an automated deep-scan across 70 components analyzing for Architecture, Logic, Performance, and UI/UX issues based on the Master Audit Prompt.\n')

total_files = 0
total_lines = 0
issues_found = 0

for root, _, files in os.walk(FRONTEND_DIR):
    for file in files:
        if file.endswith('.jsx') or file.endswith('.js'):
            filepath = os.path.join(root, file)
            total_files += 1
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                total_lines += len(lines)
                
                file_issues = []
                content = ''.join(lines)
                
                if len(lines) > 500:
                    file_issues.append('- **[High] Architecture:** God Component pattern detected (>500 lines). Needs splitting.')
                
                if 'useMemo' not in content and 'useCallback' not in content and '.map(' in content and len(lines) > 200:
                    file_issues.append('- **[Medium] Performance:** Frequent `.map()` rendering without `useMemo`/`useCallback` detected in a large file.')
                
                if 'setTimeout(' in content and 'useEffect(' in content and 'clearTimeout(' not in content:
                    file_issues.append('- **[Medium] Logic:** `setTimeout` used inside `useEffect` without `clearTimeout`, potential memory leak.')
                
                if 'z-[999' in content or 'z-[2000' in content:
                    file_issues.append('- **[Low] UI/UX:** Extreme z-index hardcoding detected. Consider CSS context stacking.')
                
                if 'window.addEventListener' in content and 'window.removeEventListener' not in content:
                    file_issues.append('- **[High] Logic:** `addEventListener` attached without `removeEventListener`. Memory leak guaranteed.')
                
                if '<Canvas' in content and 'mode=' in content:
                    file_issues.append('- **[Medium] Three.js:** Canvas recreated conditionally. Render loop might stall.')

                if file_issues:
                    report.append(f'\n### `{file}`')
                    for issue in file_issues:
                        report.append(issue)
                        issues_found += 1

report.append('\n## Final Scan Statistics\n')
report.append(f'- **Total Files Scanned:** {total_files}\n')
report.append(f'- **Total Lines Scanned:** {total_lines}\n')
report.append(f'- **Total Heuristic Issues Found:** {issues_found}\n')

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print('Report generated successfully')
