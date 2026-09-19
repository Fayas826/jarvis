import * as THREE from "three";
import { useFrame } from "@react-three/fiber";

// 🚁 KINETIC_CAMERA (Smooth Drone Perspektive)
export const KineticCamera = () => {
    useFrame((state) => {
        const t = performance.now() / 1000;
        state.camera.position.x = Math.sin(t * 0.5) * 0.5;
        state.camera.position.y = Math.cos(t * 0.3) * 0.5;
        state.camera.lookAt(0, 0, 0);
    });
    return null;
};

// 🎥 PARALLAX_CONTROLLER
export const ParallaxController = () => {
    useFrame((state) => {
        const parallaxGroup = state.scene.getObjectByName("ParallaxLayer");
        if (parallaxGroup) {
            parallaxGroup.rotation.x = THREE.MathUtils.lerp(parallaxGroup.rotation.x, -state.mouse.y * 0.2, 0.1);
            parallaxGroup.rotation.y = THREE.MathUtils.lerp(parallaxGroup.rotation.y, state.mouse.x * 0.2, 0.1);
        }
    });
    return null;
};
