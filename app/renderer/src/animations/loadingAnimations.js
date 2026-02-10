/**
 * Loading Animation Components
 * Skeleton screens, spinners, and progress indicators
 */

// Skeleton loader configurations
export const skeletonAnimations = {
  shimmer: {
    initial: { backgroundPosition: '200% 0' },
    animate: { backgroundPosition: '-200% 0' },
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear'
    }
  },
  
  pulse: {
    animate: { opacity: [0.4, 0.8, 0.4] },
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
};

// Spinner variants
export const spinnerVariants = {
  default: {
    animate: { rotate: 360 },
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear'
    }
  },
  
  bounce: {
    animate: {
      scale: [1, 1.2, 1],
      rotate: 360
    },
    transition: {
      duration: 1.2,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  dots: {
    animate: {
      opacity: [0.3, 1, 0.3]
    },
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
};

// Progress bar animations
export const progressAnimations = {
  indeterminate: {
    animate: {
      x: ['-100%', '100%']
    },
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  determinate: (progress) => ({
    animate: {
      width: `${progress}%`
    },
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  })
};

// Typing indicator (like "AI is typing...")
export const typingIndicator = {
  dot1: {
    animate: {
      y: [0, -8, 0]
    },
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: 'easeInOut',
      delay: 0
    }
  },
  
  dot2: {
    animate: {
      y: [0, -8, 0]
    },
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: 'easeInOut',
      delay: 0.1
    }
  },
  
  dot3: {
    animate: {
      y: [0, -8, 0]
    },
    transition: {
      duration: 0.6,
      repeat: Infinity,
      ease: 'easeInOut',
      delay: 0.2
    }
  }
};

// Wave loading animation
export const waveAnimation = {
  animate: (i) => ({
    scaleY: [1, 1.5, 1],
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'easeInOut',
      delay: i * 0.1
    }
  })
};

// Circular progress
export const circularProgress = (progress) => ({
  pathLength: progress / 100,
  transition: {
    duration: 0.5,
    ease: 'easeInOut'
  }
});

export default {
  skeletonAnimations,
  spinnerVariants,
  progressAnimations,
  typingIndicator,
  waveAnimation,
  circularProgress
};
