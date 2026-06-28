const context = new (window.AudioContext || window.webkitAudioContext)();
const sounds = {
  start: "/sounds/start.wav",
  activate: "/sounds/activate.wav",
  click: "/sounds/click.wav",
  scan: "/sounds/scan.wav",
  deploy: "https://cdn.pixabay.com/audio/2024/03/01/audio_f7d6b70098.mp3",
  power_down: "https://cdn.pixabay.com/audio/2024/03/01/audio_e3922d2924.mp3"
};

const audioBuffers = {};
const activeNodes = {};

// 🖖 O.M.E.G.A. XIV: PROACTIVE AUDIO RECOVERY (STABILIZATION)
const loadSounds = async () => {
    for (const [name, url] of Object.entries(sounds)) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
            const arrayBuffer = await response.arrayBuffer();
            
            // Modern Promise-based Decoding with Absolute Silencing
            try {
                const buffer = await context.decodeAudioData(arrayBuffer);
                audioBuffers[name] = buffer;
            } catch {
                // 🤫 SILENT FALLBACK: EncodingError is suppressed.
                // This means the file is incompatible with your current browser codec.
                console.log(`[Audio/Sentience] System bypass for ${name}: INCOMPATIBLE_CODEC`);
            }
        } catch (e) {
            console.warn(`[Audio/Sentience] Neural link failure for ${name}: ${e.message}`);
        }
    }
};

loadSounds();

/**
 * Play a JARVIS system sound with spatial panning
 */
export const playSound = (name, pan = 0, loop = false) => {
  if (!audioBuffers[name]) {
      // Automatic Neural Fallback (Silent resolve)
      return;
  }

  try {
      const source = context.createBufferSource();
      source.buffer = audioBuffers[name];
      source.loop = loop;

      const panner = context.createStereoPanner();
      panner.pan.value = pan;

      const gain = context.createGain();
      gain.gain.value = 0.8;

      source.connect(panner).connect(gain).connect(context.destination);
      
      if (loop) activeNodes[name] = source;
      
      source.start(0);
  } catch {
      console.warn(`[Audio] Playback Jitter: ${name}`);
  }
};

export const stopSound = (name) => {
  if (activeNodes[name]) {
    try {
      activeNodes[name].stop();
      delete activeNodes[name];
    } catch {
      delete activeNodes[name];
    }
  }
};
