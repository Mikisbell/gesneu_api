const API_BASE_URL = '/api/v1';

interface FetchOptions extends RequestInit {
    params?: Record<string, string>;
}

export async function apiClient<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { params, ...init } = options;

    let url = `${API_BASE_URL}${endpoint}`;
    if (params) {
        const searchParams = new URLSearchParams(params);
        url += `?${searchParams.toString()}`;
    }

    const response = await fetch(url, {
        ...init,
        credentials: 'include', // Ensure cookies are sent for auth
        headers: {
            'Content-Type': 'application/json',
            ...init.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `API Error: ${response.statusText}`);
    }

    const json = await response.json();
    return json.data;
}
