/**
 * Animation Transitions for AI-Lab
 * Reusable animation configurations using Framer Motion
 */

// Message animations
export const messageAnimations = {
  slideInUp: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
    transition: { duration: 0.25, ease: 'easeOut' }
  },
  
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 }
  },
  
  scaleIn: {
    initial: { scale: 0.95, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.95, opacity: 0 },
    transition: { duration: 0.2, ease: 'easeOut' }
  },
  
  slideInLeft: {
    initial: { x: -20, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: 20, opacity: 0 },
    transition: { duration: 0.25, ease: 'easeOut' }
  },
  
  slideInRight: {
    initial: { x: 20, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -20, opacity: 0 },
    transition: { duration: 0.25, ease: 'easeOut' }
  }
};

// Modal/Dialog animations
export const modalAnimations = {
  backdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.15 }
  },
  
  dialog: {
    initial: { scale: 0.95, opacity: 0, y: 10 },
    animate: { scale: 1, opacity: 1, y: 0 },
    exit: { scale: 0.95, opacity: 0, y: 10 },
    transition: { duration: 0.2, ease: 'easeOut' }
  }
};

// Dropdown/Popover animations
export const dropdownAnimations = {
  expand: {
    initial: { height: 0, opacity: 0 },
    animate: { height: 'auto', opacity: 1 },
    exit: { height: 0, opacity: 0 },
    transition: { duration: 0.2, ease: 'easeOut' }
  },
  
  slideDown: {
    initial: { y: -10, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -10, opacity: 0 },
    transition: { duration: 0.15, ease: 'easeOut' }
  }
};

// Sidebar/Drawer animations
export const sidebarAnimations = {
  slideLeft: {
    initial: { x: '-100%' },
    animate: { x: 0 },
    exit: { x: '-100%' },
    transition: { duration: 0.3, ease: 'easeInOut' }
  },
  
  slideRight: {
    initial: { x: '100%' },
    animate: { x: 0 },
    exit: { x: '100%' },
    transition: { duration: 0.3, ease: 'easeInOut' }
  }
};

// Loading animations
export const loadingAnimations = {
  pulse: {
    animate: { 
      scale: [1, 1.05, 1],
      opacity: [0.5, 1, 0.5]
    },
    transition: { 
      duration: 1.5, 
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  spin: {
    animate: { rotate: 360 },
    transition: { 
      duration: 1, 
      repeat: Infinity,
      ease: 'linear'
    }
  },
  
  shimmer: {
    animate: {
      backgroundPosition: ['200% 0', '-200% 0']
    },
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear'
    }
  }
};

// Button/Interactive animations
export const interactiveAnimations = {
  tap: {
    whileTap: { scale: 0.95 },
    transition: { duration: 0.1 }
  },
  
  hover: {
    whileHover: { scale: 1.02 },
    transition: { duration: 0.15 }
  },
  
  focus: {
    whileFocus: { 
      boxShadow: '0 0 0 3px var(--color-focus)',
      scale: 1.01
    },
    transition: { duration: 0.15 }
  }
};

// List/Stagger animations
export const listAnimations = {
  container: {
    animate: {
      transition: {
        staggerChildren: 0.05
      }
    }
  },
  
  item: {
    initial: { y: 10, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    transition: { duration: 0.2 }
  }
};

// Page transition animations
export const pageAnimations = {
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  
  slideUp: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 },
    transition: { duration: 0.3 }
  }
};

// Utility function to create custom transitions
export const createTransition = (duration = 0.25, ease = 'easeOut') => ({
  duration,
  ease
});

// Utility function for spring animations
export const springTransition = (stiffness = 300, damping = 30) => ({
  type: 'spring',
  stiffness,
  damping
});

export default {
  messageAnimations,
  modalAnimations,
  dropdownAnimations,
  sidebarAnimations,
  loadingAnimations,
  interactiveAnimations,
  listAnimations,
  pageAnimations,
  createTransition,
  springTransition
};
