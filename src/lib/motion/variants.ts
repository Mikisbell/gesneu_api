/**
 * 🎬 Framer Motion Variants Library
 * Professional animation presets for consistent UX
 */

import { Variants } from 'framer-motion'

// ============================================
// PAGE TRANSITIONS
// ============================================

export const pageVariants: Variants = {
    initial: {
        opacity: 0,
        y: 20,
    },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.3,
            ease: [0.16, 1, 0.3, 1], // Custom easing
        },
    },
    exit: {
        opacity: 0,
        y: -20,
        transition: {
            duration: 0.2,
            ease: [0.4, 0, 1, 1],
        },
    },
}

// ============================================
// CARD ANIMATIONS
// ============================================

export const cardVariants: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.95,
    },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            type: 'spring',
            stiffness: 300,
            damping: 30,
        },
    },
    hover: {
        scale: 1.02,
        boxShadow: '0 10px 20px rgba(0,0,0,0.1)',
        transition: {
            type: 'spring',
            stiffness: 400,
            damping: 20,
        },
    },
    tap: {
        scale: 0.98,
    },
}

// ============================================
// LIST STAGGER
// ============================================

export const listContainerVariants: Variants = {
    hidden: {
        opacity: 0,
    },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.07,
            delayChildren: 0.1,
        },
    },
}

export const listItemVariants: Variants = {
    hidden: {
        opacity: 0,
        x: -20,
    },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            type: 'spring',
            stiffness: 300,
            damping: 24,
        },
    },
}

// ============================================
// MODAL/DIALOG
// ============================================

export const modalOverlayVariants: Variants = {
    hidden: {
        opacity: 0,
    },
    visible: {
        opacity: 1,
        transition: {
            duration: 0.2,
        },
    },
    exit: {
        opacity: 0,
        transition: {
            duration: 0.15,
        },
    },
}

export const modalContentVariants: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.9,
        y: 20,
    },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            type: 'spring',
            stiffness: 300,
            damping: 30,
        },
    },
    exit: {
        opacity: 0,
        scale: 0.9,
        y: 20,
        transition: {
            duration: 0.15,
        },
    },
}

// ============================================
// SLIDE ANIMATIONS
// ============================================

export const slideInVariants: Variants = {
    hidden: {
        x: '100%',
    },
    visible: {
        x: 0,
        transition: {
            type: 'spring',
            stiffness: 300,
            damping: 30,
        },
    },
    exit: {
        x: '100%',
        transition: {
            duration: 0.2,
        },
    },
}

// ============================================
// NOTIFICATION / TOAST
// ============================================

export const toastVariants: Variants = {
    hidden: {
        opacity: 0,
        y: -50,
        scale: 0.3,
    },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            type: 'spring',
            stiffness: 500,
            damping: 40,
        },
    },
    exit: {
        opacity: 0,
        scale: 0.5,
        transition: {
            duration: 0.2,
        },
    },
}

// ============================================
// FADE ANIMATIONS
// ============================================

export const fadeInVariants: Variants = {
    hidden: {
        opacity: 0,
    },
    visible: {
        opacity: 1,
        transition: {
            duration: 0.2,
        },
    },
    exit: {
        opacity: 0,
        transition: {
            duration: 0.15,
        },
    },
}

// ============================================
// BOUNCE ANIMATION
// ============================================

export const bounceVariants: Variants = {
    initial: {
        y: 0,
    },
    animate: {
        y: [0, -10, 0],
        transition: {
            duration: 0.6,
            repeat: Infinity,
            repeatDelay: 2,
        },
    },
}

// ============================================
// SKELETON PULSE
// ============================================

export const skeletonVariants: Variants = {
    initial: {
        opacity: 0.5,
    },
    animate: {
        opacity: [0.5, 1, 0.5],
        transition: {
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
        },
    },
}
