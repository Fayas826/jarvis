import os
import re

# Fix useBiometricState.js
p = r"C:\jarvis AI\jarvis\frontend\src\hooks\useBiometricState.js"
with open(p, 'r') as f: c = f.read()
c = c.replace("useRef", "")
c = re.sub(r'const setGlobalResonanceUrl = useCallback\(\(\) => \{\}, \[\]\);.*?\n', '', c)
with open(p, 'w') as f: f.write(c)

# Fix useSystemSentinels.js
p = r"C:\jarvis AI\jarvis\frontend\src\hooks\useSystemSentinels.js"
with open(p, 'r') as f: c = f.read()
c = c.replace(", useCallback", "")
with open(p, 'w') as f: f.write(c)

# Fix useVoiceState.js
p = r"C:\jarvis AI\jarvis\frontend\src\hooks\useVoiceState.js"
with open(p, 'r') as f: c = f.read()
c = c.replace("setIsVisionActive, ", "").replace("PROFILES, profile, settings, ", "")
with open(p, 'w') as f: f.write(c)

# Fix AppStateProvider.jsx
p = r"C:\jarvis AI\jarvis\frontend\src\core\AppStateProvider.jsx"
with open(p, 'r') as f: lines = f.readlines()

new_lines = []
for line in lines:
    if "const activityTimerRef = useRef({ lastActive: Date.now(), notified: false });" in line:
        new_lines.append("  const activityTimerRef = useRef(null);\n")
        new_lines.append("  if (!activityTimerRef.current) activityTimerRef.current = { lastActive: Date.now(), notified: false };\n")
    elif "window.jarvis_test_ignite = initializeSystem;" in line:
        new_lines.append("  useEffect(() => { window.jarvis_test_ignite = initializeSystem; }, [initializeSystem]);\n")
    elif "window.verifyMultimodalTruth = verifyMultimodalTruth;" in line:
        new_lines.append("  useEffect(() => { window.verifyMultimodalTruth = verifyMultimodalTruth; }, [verifyMultimodalTruth]);\n")
    elif "const aiStateWithSpeak = {" in line:
        new_lines.append("  const aiStateWithSpeak = React.useMemo(() => ({\n")
    elif "...ai," in line:
        new_lines.append(line)
    elif "speak," in line and "aiStateWithSpeak" not in line and "const speak =" not in line:
        new_lines.append(line)
    elif "processLocalIntent: processLocalIntentWithSingularity," in line:
        new_lines.append(line)
    elif "toggleSingularity: () => processLocalIntentWithSingularity(\"engage omega protocol\")" in line:
        new_lines.append(line)
    elif "};" in line and len(new_lines) > 0 and "toggleSingularity:" in new_lines[-1]:
        new_lines.append("  }), [ai, speak, processLocalIntentWithSingularity]);\n")
    else:
        new_lines.append(line)

content = "".join(new_lines)
# Fix dependency arrays
content = re.sub(r'\[ui\.PROFILES, ui\.profile, ui\.settings\.volume, ai, addLog, ui\]', '[ai, addLog, ui]', content)
content = re.sub(r'\[ui, healthState, worldState, agentState, actionResults, addLog, handleLogoComplete, handleAssemblyComplete, runAgentMission\]', '[ui, healthState, worldState, agentState, actionResults, addLog, handleLogoComplete, handleAssemblyComplete, runAgentMission, initializeSystem]', content)

with open(p, 'w') as f: f.write(content)
