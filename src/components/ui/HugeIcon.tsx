import React from 'react';

interface HugeIconProps extends React.HTMLAttributes<HTMLElement> {
    name: string;
    variant?: 'stroke' | 'duotone' | 'twotone' | 'bulk' | 'solid';
    size?: number;
    className?: string;
}

/**
 * Componente base para iconos HugeIcons.
 * Requiere que el CSS esté cargado en layout.tsx.
 * 
 * @example
 * <HugeIcon name="tire" size={24} />
 * // Render: <i class="hgi-stroke hgi-tire text-2xl"></i>
 */
export const HugeIcon = ({ name, variant = 'stroke', size = 24, className = '', ...props }: HugeIconProps) => {
    // Mapeo simple de tamaño a clases Tailwind (aproximado) si se quisiera usar clases
    // pero aquí usamos style fontSize para precisión

    const baseClass = `hgi-${variant}`;
    const iconClass = `hgi-${name}`;

    return (
        <i
            className={`${baseClass} ${iconClass} ${className}`}
            style={{ fontSize: size }}
            {...props}
        />
    );
};
