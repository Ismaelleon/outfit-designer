import { Pressable, Text, TextInput, View } from "react-native";
import { useAuth } from "../AuthContext";
import { useState } from "react";

export default function SignUp({ navigation }) {
    const [name, setName] = useState("");
    const [password, setPassword] = useState("");
    const { onSignup } = useAuth();

    async function signUp() {
        await onSignup(name, password);
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
                onPress={() => signUp()}
            >
                <Text className="text-sm text-white font-bold">Sign Up</Text>
            </Pressable>
            <Pressable
                className="mt-4"
                onPress={() => {
                    navigation.navigate("Index");
                }}
            >
                <Text className="text-neutral-800">
                    Already have an account? Log In
                </Text>
            </Pressable>
        </View>
    );
}
