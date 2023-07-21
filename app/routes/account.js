import { Pressable, Text, View } from "react-native";
import Header from "../components/header";
import Navigation from "../components/navigation";
import { useAuth } from "../AuthContext";

export default function Account() {
    const { onLogout } = useAuth();

    async function logOut() {
        await onLogout();
    }

    return (
        <View className="h-screen">
            <Header />
            <View>
                <Pressable className="px-4 py-3 border-b border-neutral-200 bg-white">
                    <Text className="text-base text-red-500">
                        Delete Account
                    </Text>
                </Pressable>
                <Pressable
                    className="px-4 py-3 border-b border-neutral-200 bg-white"
                    onPress={logOut}
                >
                    <Text className="text-base">Log Out</Text>
                </Pressable>
            </View>
            <Navigation />
        </View>
    );
}
