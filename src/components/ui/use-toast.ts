export const useToast = () => {
    return {
        toast: ({ title, description, variant }: { title: string; description?: string; variant?: 'default' | 'destructive' }) => {
            const message = description ? `${title}\n${description}` : title;
            if (typeof window !== 'undefined') {
                if (variant === 'destructive') {
                    window.alert(`❌ ${message}`);
                } else {
                    window.alert(`✅ ${message}`);
                }
            }
        },
    };
};
