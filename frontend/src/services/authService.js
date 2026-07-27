import api from './api'; // Importamos la configuración de axios que ya tienes

// Función para Iniciar Sesión
export const loginUsuario = async (email, password) => {
    try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await api.post('/api/v1/token', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });

        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || "Error al iniciar sesión";
    }
};

// Función para Registrar Usuario (La que preguntaste)
export const registrarUsuario = async (userData) => {
    try {
        const response = await api.post('/api/v1/register', userData);
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || "Error en el registro";
    }
};