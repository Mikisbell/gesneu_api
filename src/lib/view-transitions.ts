/**
 * 🎭 View Transitions API Utilities
 * Native browser animations for page transitions
 */

type ViewTransitionCallback = () => void | Promise<void>

/**
 * Wraps a callback in a View Transition
 * Falls back to regular execution if not supported
 */
export function withViewTransition(callback: ViewTransitionCallback) {
    if (typeof document !== 'undefined' && 'startViewTransition' in document) {
        return (document as any).startViewTransition(callback)
    }

    // Fallback for browsers that don't support View Transitions
    return Promise.resolve(callback())
}

/**
 * Hook for using View Transitions in React components
 */
export function useViewTransition() {
    const transition = (callback: ViewTransitionCallback) => {
        return withViewTransition(callback)
    }

    const isSupported = typeof document !== 'undefined' && 'startViewTransition' in document

    return { transition, isSupported }
}

/**
 * Create a named view transition for specific elements
 * Usage: Add view-transition-name to elements in CSS
 */
export function createNamedTransition(name: string, callback: ViewTransitionCallback) {
    if (typeof document !== 'undefined' && 'startViewTransition' in document) {
        const transition = (document as any).startViewTransition(callback)

        // You can customize per-name animations in CSS
        return transition
    }

    return Promise.resolve(callback())
}
