'use client';

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

// Registrar componentes de Chart.js
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement
);

// Estilos globales para los charts
const chartColors = {
    primary: 'rgba(59, 130, 246, 0.8)',
    secondary: 'rgba(16, 185, 129, 0.8)',
    warning: 'rgba(245, 158, 11, 0.8)',
    danger: 'rgba(239, 68, 68, 0.8)',
    info: 'rgba(139, 92, 246, 0.8)',
    gray: 'rgba(107, 114, 128, 0.8)',
};

interface BarChartProps {
    labels: string[];
    data: number[];
    title: string;
    color?: string;
}

export function BarChart({ labels, data, title, color = chartColors.primary }: BarChartProps) {
    const chartData = {
        labels,
        datasets: [{
            label: title,
            data,
            backgroundColor: color,
            borderRadius: 4,
        }],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: true, text: title, font: { size: 14 } },
        },
        scales: {
            y: { beginAtZero: true },
        },
    };

    return <Bar data={chartData} options={options} />;
}

interface DoughnutChartProps {
    labels: string[];
    data: number[];
    title: string;
    colors?: string[];
}

export function DoughnutChart({ labels, data, title, colors }: DoughnutChartProps) {
    const defaultColors = [
        chartColors.primary,
        chartColors.secondary,
        chartColors.warning,
        chartColors.danger,
        chartColors.info,
        chartColors.gray,
    ];

    const chartData = {
        labels,
        datasets: [{
            data,
            backgroundColor: colors || defaultColors.slice(0, data.length),
            borderWidth: 2,
            borderColor: '#fff',
        }],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { position: 'bottom' as const },
            title: { display: true, text: title, font: { size: 14 } },
        },
    };

    return <Doughnut data={chartData} options={options} />;
}

interface LineChartProps {
    labels: string[];
    data: number[];
    title: string;
    color?: string;
}

export function LineChart({ labels, data, title, color = chartColors.primary }: LineChartProps) {
    const chartData = {
        labels,
        datasets: [{
            label: title,
            data,
            borderColor: color,
            backgroundColor: color.replace('0.8', '0.2'),
            tension: 0.3,
            fill: true,
        }],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: true, text: title, font: { size: 14 } },
        },
        scales: {
            y: { beginAtZero: true },
        },
    };

    return <Line data={chartData} options={options} />;
}

// Componente de KPI Card
interface KpiCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: 'up' | 'down' | 'neutral';
    color?: 'blue' | 'green' | 'yellow' | 'red';
}

export function KpiCard({ title, value, subtitle, trend, color = 'blue' }: KpiCardProps) {
    const colorClasses = {
        blue: 'bg-blue-50 border-blue-200 text-blue-700',
        green: 'bg-green-50 border-green-200 text-green-700',
        yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
        red: 'bg-red-50 border-red-200 text-red-700',
    };

    const trendIcons = {
        up: '↑',
        down: '↓',
        neutral: '→',
    };

    return (
        <div className={`p-4 rounded-lg border-2 ${colorClasses[color]}`}>
            <p className="text-sm font-medium opacity-80">{title}</p>
            <p className="text-2xl font-bold mt-1">
                {value}
                {trend && <span className="text-sm ml-2">{trendIcons[trend]}</span>}
            </p>
            {subtitle && <p className="text-xs mt-1 opacity-60">{subtitle}</p>}
        </div>
    );
}

export { chartColors };
