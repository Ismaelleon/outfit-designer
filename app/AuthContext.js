import axios from "axios";
import { createContext, useContext, useEffect, useState } from "react";
import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "jwt";
export const API_URL = "http://192.168.1.9:8080";
const AuthContext = createContext({});

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [authState, setAuthState] = useState({
        token: null,
        authenticated: null,
    });

    useEffect(() => {
        async function loadToken() {
            const token = await SecureStore.getItemAsync(TOKEN_KEY);
            console.log("stored:", token);

            if (token) {
                axios.defaults.headers.common[
                    "Authorization"
                ] = `Bearer ${token}`;

                setAuthState({
                    token,
                    authenticated: true,
                });
            }
        }

        loadToken();
    }, []);

    async function signUp(name, password) {
        try {
            const result = await axios.post(`${API_URL}/sign-up`, {
                name,
                password,
            });

            await logIn(name, password);
        } catch (error) {
            console.log(error);
        }
    }

    async function logIn(name, password) {
        try {
            const result = await axios.post(`${API_URL}/log-in`, {
                name,
                password,
            });

            setAuthState({
                token: result.data.token,
                authenticated: true,
            });

            axios.defaults.headers.common[
                "Authorization"
            ] = `Bearer ${result.data.token}`;

            await SecureStore.setItemAsync(TOKEN_KEY, result.data.token);

            return result;
        } catch (error) {
            console.log(error);
        }
    }

    async function logOut() {
        await SecureStore.deleteItemAsync(TOKEN_KEY);

        axios.defaults.headers.common["Authorization"] = "";

        setAuthState({
            token: null,
            authenticated: false,
        });
    }

    const value = {
        onSignup: signUp,
        onLogin: logIn,
        onLogout: logOut,
        authState,
    };

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}
