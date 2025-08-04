import React, { useRef, useEffect } from 'react';
import { DotLottie } from '@lottiefiles/dotlottie-web';

const LottieAnimation = () => {
  // 1. Create a ref for the canvas element
  const canvasRef = useRef(null);

  // 2. Use useEffect to run code after the component mounts
  useEffect(() => {
    // Make sure the canvas ref is not null
    if (canvasRef.current) {
      const dotLottie = new DotLottie({
        autoplay: true,
        loop: true,
        // 3. Pass the ref's 'current' value to the canvas property
        canvas: canvasRef.current,
        src: '/loading-animation.lottie',
      });

      // Optional: Cleanup function to destroy the animation when the component unmounts
      return () => {
        dotLottie.destroy();
      };
    }
  }, []); // The empty array ensures this effect runs only once

  return (
    // 4. Assign the ref to your canvas element
    <canvas ref={canvasRef} style={{ width: '150px', height: '150px'}} />
  );
};

export default LottieAnimation;