import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

export default function ParticlesBg() {
  const particlesInit = async (main) => {
    await loadFull(main);
  };

  return (
    <Particles
      init={particlesInit}
      options={{
        background: { color: "transparent" },
        particles: {
          number: { value: 50 },
          color: { value: "#00bfff" },
          links: { enable: true, color: "#00bfff", opacity: 0.2 },
          move: { enable: true, speed: 1 },
          opacity: { value: 0.5 },
          size: { value: 2 }
        },
      }}
      className="absolute top-0 left-0 w-full h-full -z-10"
    />
  );
}
