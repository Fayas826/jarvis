try:
    from crewai.tools import tool
    print("SUCCESS: crewai.tools")
except Exception as e:
    print(f"FAILED: crewai.tools: {e}")

try:
    from crewai_tools import tool
    print("SUCCESS: crewai_tools")
except Exception as e:
    print(f"FAILED: crewai_tools: {e}")

try:
    import crewai_tools
    print("crewai_tools dir:", dir(crewai_tools))
except Exception as e:
    print("FAILED import crewai_tools:", e)
