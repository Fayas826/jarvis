#include <cmath>
#include <cstdint>

extern "C" {

    struct AudioMetrics {
        double rms;
        int zcr;
        bool is_voice;
    };

    // Calculate metrics on a chunk of 16-bit PCM audio
    __declspec(dllexport) AudioMetrics process_audio_chunk(const int16_t* buffer, int length) {
        if (length == 0 || buffer == nullptr) {
            return {0.0, 0, false};
        }

        double sum_squares = 0.0;
        int zcr = 0;
        
        for (int i = 0; i < length; ++i) {
            double sample = static_cast<double>(buffer[i]) / 32768.0; // Normalize to -1.0 to 1.0
            sum_squares += sample * sample;
            
            if (i > 0) {
                bool current_pos = buffer[i] > 0;
                bool prev_pos = buffer[i - 1] > 0;
                if (current_pos != prev_pos) {
                    zcr++;
                }
            }
        }

        double rms = std::sqrt(sum_squares / length) * 100.0;
        
        // Simple VAD logic: Voice usually has some energy and a certain ZCR range.
        // These thresholds would be tuned in production.
        bool is_voice = (rms > 1.5) && (zcr > (length / 50)) && (zcr < (length / 4));

        return {rms, zcr, is_voice};
    }
}
