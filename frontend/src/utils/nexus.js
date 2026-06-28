/**
 * 🧬 O.M.E.G.A. XXXXIX: NEURAL_GATEWAY_RESONATOR [V19.1]
 * Universal utility for dynamic API routing via the 'Lighthouse' protocol.
 */

// 🌐 AUTO_DETECT_HOST: Resolve host IP from window location if on mobile
const getLocalHost = () => {
    const host = window.location.hostname;
    
    // 🧬 O.M.E.G.A. LXXVII: TUNNEL_AWARENESS
    if (host.includes('lhr.life') || host.includes('trycloudflare.com') || host.includes('loca.lt')) {
        // Sir, for this mission we are utilizing a dual-tunnel resonance.
        // We override to the specific secure backend node.
        return "https://jarvis-omega-zenith.loca.lt";
    }

    // Default to the Vite proxy in development
    return "/api";
};

let API_BASE_URL = getLocalHost();

export const loadNexusConfig = async () => {
    try {
        console.log("[NEXUS] Searching for Neural Lighthouse...");
        const response = await fetch(`/config.json?v=${Date.now()}`);
        if (!response.ok) throw new Error("LIGHTHOUSE_OFFLINE");
        
        const config = await response.json();
        let potentialUrl = config.API_BASE_URL || getLocalHost();

        // 🧬 V38.1: NEURAL_PING (Verify tunnel reachability before adoption)
        if (potentialUrl.includes("trycloudflare.com")) {
            try {
                // 🧬 O.M.E.G.A. FAST_PATH: Reduced timeout for instant bridge verification
                const pulse = await fetch(`${potentialUrl}/resonance/vitals`, { signal: AbortSignal.timeout(1000) });
                if (!pulse.ok) throw new Error("TUNNEL_DEAD");
                API_BASE_URL = potentialUrl;
                console.log(`[NEXUS] Neural Bridge Established & Verified: ${API_BASE_URL}`);
            } catch {
                console.warn("[NEXUS] Discovered Bridge is non-responsive. Falling back to Local Resonance.");
                API_BASE_URL = getLocalHost();
            }
        } else {
            API_BASE_URL = potentialUrl;
        }
    } catch {
        console.warn("[NEXUS] Lighthouse failed. Defaulting to Local Resonance.");
        API_BASE_URL = getLocalHost();
    }
};

export const getApiBaseUrl = () => {
    return API_BASE_URL;
};

export const nexusConfig = {
    headers: {
        'bypass-tunnel-reminder': 'true'
    }
};
