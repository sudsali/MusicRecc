"use client";
import { cn } from "../../lib/utils";
import React, { useEffect, useRef } from "react";
import { createNoise3D } from "simplex-noise";

export const AtmosphericBackground = ({
  children,
  className,
  containerClassName,
  baseColor = "#000000",
  highlightColor = "#1e40af",
  noiseScale = 0.5,
  speed = "fast",
  ...props
}) => {
  const noise = createNoise3D();
  const canvasRef = useRef(null);
  const timeRef = useRef(0);
  const frameCountRef = useRef(0);
  const grainTextureRef = useRef(null);
  
  const getSpeed = () => {
    switch (speed) {
      case "slow":
        return 0.0002;
      case "fast":
        return 0.001;
      default:
        return 0.0002;
    }
  };

  // Create grain texture function
  const createGrainTexture = (width, height) => {
    const grainCanvas = document.createElement('canvas');
    const grainCtx = grainCanvas.getContext('2d');
    grainCanvas.width = width;
    grainCanvas.height = height;
    
    const imageData = grainCtx.createImageData(width, height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
      const noise = Math.random() - 0.5;
      const value = noise * 20; // grain intensity
      
      data[i] = value;     // R
      data[i + 1] = value; // G
      data[i + 2] = value; // B
      data[i + 3] = 25;    // Alpha
    }
    
    grainCtx.putImageData(imageData, 0, 0);
    return grainCanvas;
  };

  const init = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const w = canvas.width = window.innerWidth;
    const h = canvas.height = window.innerHeight;

    // Create offscreen canvas for noise
    const noiseCanvas = document.createElement('canvas');
    const noiseCtx = noiseCanvas.getContext('2d');
    const scale = 4; // Reduce resolution for better performance
    noiseCanvas.width = w / scale;
    noiseCanvas.height = h / scale;

    // Create initial grain texture
    grainTextureRef.current = createGrainTexture(w, h);

    const drawNoise = () => {
      frameCountRef.current++;
      
      // Update only every other frame
      if (frameCountRef.current % 2 === 0) {
        const imageData = noiseCtx.createImageData(noiseCanvas.width, noiseCanvas.height);
        const data = imageData.data;
        
        timeRef.current += getSpeed();
        
        for (let x = 0; x < noiseCanvas.width; x++) {
          for (let y = 0; y < noiseCanvas.height; y++) {
            const value = noise(
              x * 0.008 * noiseScale,
              y * 0.008 * noiseScale,
              timeRef.current
            );
            
            const idx = (x + y * noiseCanvas.width) * 4;
            const gradient = (y / noiseCanvas.height);
            const normalizedValue = ((value + 1) / 2) - 0.5;
            
            const r = lerp(0, 20, normalizedValue + gradient);
            const g = lerp(0, 83, normalizedValue + gradient);
            const b = lerp(0, 45, normalizedValue + gradient);
            
            data[idx] = r;
            data[idx + 1] = g;
            data[idx + 2] = b;
            data[idx + 3] = 255;
          }
        }
        
        noiseCtx.putImageData(imageData, 0, 0);
        
        // Draw scaled noise to main canvas
        ctx.clearRect(0, 0, w, h);
        ctx.drawImage(noiseCanvas, 0, 0, w, h);
        
        // Add grain
        ctx.globalCompositeOperation = 'overlay';
        ctx.globalAlpha = 0.15;
        ctx.drawImage(grainTextureRef.current, 0, 0);
        ctx.globalCompositeOperation = 'source-over';
        ctx.globalAlpha = 1.0;
      }
      
      requestAnimationFrame(drawNoise);
    };

    drawNoise();
  };

  // Linear interpolation helper
  const lerp = (start, end, amt) => {
    return (1 - amt) * start + amt * end;
  };

  useEffect(() => {
    init();
    
    const handleResize = () => {
      const canvas = canvasRef.current;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      // Recreate grain texture at new size
      grainTextureRef.current = createGrainTexture(canvas.width, canvas.height);
    };

    const debouncedResize = debounce(handleResize, 250);
    window.addEventListener('resize', debouncedResize);
    
    return () => {
      window.removeEventListener('resize', debouncedResize);
    };
  }, []);

  // Simple debounce function
  const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  return (
    <div className={cn("h-screen flex flex-col items-center justify-center", containerClassName)}>
      <canvas
        className="absolute inset-0 z-0"
        ref={canvasRef}
        style={{ filter: 'blur(10px)' }}
      />
      <div className={cn("relative z-10", className)} {...props}>
        {children}
      </div>
    </div>
  );
};
