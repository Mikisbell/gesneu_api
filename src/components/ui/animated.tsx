/**
 * 🎨 Modern UI Components (2026)
 * Professional components with Framer Motion
 */

'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import {
    cardVariants,
    fadeInVariants,
    listContainerVariants,
    listItemVariants,
    skeletonVariants,
} from '@/lib/motion/variants'

// ============================================
// ANIMATED CARD
// ============================================

interface AnimatedCardProps {
    children: ReactNode
    className?: string
    delay?: number
}

export function AnimatedCard({ children, className, delay = 0 }: AnimatedCardProps) {
    return (
        <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            whileHover="hover"
            whileTap="tap"
            transition={{ delay }}
            className={className}
        >
            {children}
        </motion.div>
    )
}

// ============================================
// EMPTY STATE (with animation)
// ============================================

interface EmptyStateProps {
    icon: ReactNode
    title: string
    description: string
    action?: ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
    return (
        <motion.div
            variants={fadeInVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
        >
            <Card className="border-dashed">
                <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{
                            type: 'spring',
                            stiffness: 260,
                            damping: 20,
                            delay: 0.1,
                        }}
                        className="rounded-full bg-muted p-3 mb-4"
                    >
                        {icon}
                    </motion.div>
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <CardTitle className="mb-2">{title}</CardTitle>
                        <CardDescription className="mb-6 max-w-sm">{description}</CardDescription>
                        {action && <div>{action}</div>}
                    </motion.div>
                </CardContent>
            </Card>
        </motion.div>
    )
}

// ============================================
// SKELETON TABLE (animated)
// ============================================

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
    return (
        <motion.div
            variants={listContainerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-3"
        >
            {Array.from({ length: rows }).map((_, i) => (
                <motion.div
                    key={i}
                    variants={listItemVariants}
                    className="flex items-center space-x-4"
                >
                    <Skeleton className="h-12 w-12 rounded-full" />
                    <div className="space-y-2 flex-1">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-3/4" />
                    </div>
                </motion.div>
            ))}
        </motion.div>
    )
}

// ============================================
// PAGE HEADER (animated)
// ============================================

interface PageHeaderProps {
    title: string
    description?: string
    action?: ReactNode
}

export function PageHeader({ title, description, action }: PageHeaderProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex items-start justify-between mb-6"
        >
            <div className="space-y-1">
                <motion.h1
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-3xl font-bold tracking-tight"
                >
                    {title}
                </motion.h1>
                {description && (
                    <motion.p
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.15 }}
                        className="text-muted-foreground"
                    >
                        {description}
                    </motion.p>
                )}
            </div>
            {action && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring' }}
                >
                    {action}
                </motion.div>
            )}
        </motion.div>
    )
}

// ============================================
// ANIMATED LIST
// ============================================

interface AnimatedListProps {
    children: ReactNode
    className?: string
}

export function AnimatedList({ children, className }: AnimatedListProps) {
    return (
        <motion.div
            variants={listContainerVariants}
            initial="hidden"
            animate="visible"
            className={className}
        >
            {children}
        </motion.div>
    )
}

interface AnimatedListItemProps {
    children: ReactNode
    className?: string
}

export function AnimatedListItem({ children, className }: AnimatedListItemProps) {
    return (
        <motion.div variants={listItemVariants} className={className}>
            {children}
        </motion.div>
    )
}

// ============================================
// FADE IN WRAPPER
// ============================================

interface FadeInProps {
    children: ReactNode
    delay?: number
    className?: string
}

export function FadeIn({ children, delay = 0, className }: FadeInProps) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, delay }}
            className={className}
        >
            {children}
        </motion.div>
    )
}
