import { useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useAuth } from "../AuthContext";

export default function Index({ navigation }) {
    const [name, setName] = useState("");
    const [password, setPassword] = useState("");
    const { onLogin } = useAuth();

    async function logIn() {
        const result = await onLogin(name, password);
    }

    return (
        <View className="flex justify-center items-center h-screen">
            <Text className="text-2xl font-bold mb-4">Outfit Designer</Text>
            <TextInput
                className="py-1 px-3 border rounded-sm border-neutral-200 text-sm w-2/3 focus:border-neutral-800"
                placeholder="Username"
                onChangeText={setName}
                value={name}
            />
            <TextInput
                className="py-1 px-3 border rounded-sm border-neutral-200 text-sm w-2/3 focus:border-neutral-800 my-4"
                placeholder="Password"
                secureTextEntry={true}
                onChangeText={setPassword}
                value={password}
            />
            <Pressable
                className="py-3 px-3 rounded-sm flex justify-center items-center w-2/3 bg-neutral-800"
                onPress={() => logIn()}
            >
                <Text className="text-sm text-white font-bold">Log In</Text>
            </Pressable>
            <Pressable
                className="mt-4"
                onPress={() => navigation.navigate("Sign Up")}
            >
                <Text className="text-neutral-800">
                    New here? Create an account
                </Text>
            </Pressable>
        </View>
    );
}
