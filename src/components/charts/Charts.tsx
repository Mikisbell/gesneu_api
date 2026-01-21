'use client';

import {
    BarChart as RechartsBarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart as RechartsLineChart,
    Line,
    Area,
    AreaChart
} from 'recharts';

// Estilos globales para los charts
const chartColors = {
    primary: '#3b82f6',
    secondary: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#8b5cf6',
    gray: '#6b7280',
};

const COLORS = [
    chartColors.primary,
    chartColors.secondary,
    chartColors.warning,
    chartColors.danger,
    chartColors.info,
    chartColors.gray,
];

interface BarChartProps {
    labels: string[];
    data: number[];
    title: string;
    color?: string;
}

export function BarChart({ labels, data, title, color = chartColors.primary }: BarChartProps) {
    const chartData = labels.map((label, index) => ({
        name: label,
        value: data[index],
    }));

    return (
        <div className="w-full h-64">
            <p className="text-sm font-medium text-center mb-2">{title}</p>
            <ResponsiveContainer width="100%" height="90%">
                <RechartsBarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
                </RechartsBarChart>
            </ResponsiveContainer>
        </div>
    );
}

interface DoughnutChartProps {
    labels: string[];
    data: number[];
    title: string;
    colors?: string[];
}

export function DoughnutChart({ labels, data, title, colors }: DoughnutChartProps) {
    const chartData = labels.map((label, index) => ({
        name: label,
        value: data[index],
    }));

    const fillColors = colors || COLORS.slice(0, data.length);

    return (
        <div className="w-full h-64">
            <p className="text-sm font-medium text-center mb-2">{title}</p>
            <ResponsiveContainer width="100%" height="90%">
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        paddingAngle={2}
                        dataKey="value"
                        label={({ name, percent = 0 }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                    >
                        {chartData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={fillColors[index % fillColors.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}

interface LineChartProps {
    labels: string[];
    data: number[];
    title: string;
    color?: string;
}

export function LineChart({ labels, data, title, color = chartColors.primary }: LineChartProps) {
    const chartData = labels.map((label, index) => ({
        name: label,
        value: data[index],
    }));

    return (
        <div className="w-full h-64">
            <p className="text-sm font-medium text-center mb-2">{title}</p>
            <ResponsiveContainer width="100%" height="90%">
                <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        fill={color}
                        fillOpacity={0.2}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}

// Componente de KPI Card (sin cambios, no usa chart.js)
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
