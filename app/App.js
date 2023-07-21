import { DrawerRouter, NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { AuthProvider, useAuth } from "./AuthContext";

import Index from "./routes/index";
import Closet from "./routes/closet";
import Home from "./routes/home";
import SignUp from "./routes/sign-up";
import { StatusBar } from "expo-status-bar";
import Account from "./routes/account";

const Stack = createNativeStackNavigator();

export default function App() {
    return (
        <AuthProvider>
            <StatusBar backgroundColor="#fff" translucent={false} />
            <Layout />
        </AuthProvider>
    );
}

function AppStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
                animation: "fade",
            }}
        >
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="Closet" component={Closet} />
            <Stack.Screen name="Account" component={Account} />
        </Stack.Navigator>
    );
}

function AuthStack() {
    return (
        <Stack.Navigator
            screenOptions={{ headerShown: false, animation: "none" }}
        >
            <Stack.Screen name="Index" component={Index} />
            <Stack.Screen name="Sign Up" component={SignUp} />
        </Stack.Navigator>
    );
}

function Layout() {
    const { authState, onLogout } = useAuth();

    return (
        <NavigationContainer>
            {authState.authenticated ? <AppStack /> : <AuthStack />}
        </NavigationContainer>
    );
}
