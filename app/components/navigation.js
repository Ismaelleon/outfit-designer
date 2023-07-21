import { useNavigation, useRoute } from "@react-navigation/native";
import { Pressable, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";

export default function Navigation() {
    const route = useRoute();
    const navigation = useNavigation();

    return (
        <View className="flex flex-row z-10 justify-around absolute left-0 bottom-0 w-screen border-t border-neutral-200">
            <Pressable
                className="flex flex-col items-center p-3"
                onPress={() => navigation.navigate("Home")}
            >
                <Ionicons
                    name={route.name === "Home" ? "home" : "home-outline"}
                    size={24}
                    color="#262626"
                />
                <Text
                    className={`text-sm text-neutral-800 ${
                        route.name === "Home" ? "font-bold" : ""
                    }`}
                >
                    Home
                </Text>
            </Pressable>
            <Pressable
                className="flex flex-col items-center p-3"
                onPress={() => navigation.navigate("Closet")}
            >
                <Ionicons
                    name={route.name === "Closet" ? "shirt" : "shirt-outline"}
                    size={24}
                    color="#262626"
                />
                <Text
                    className={`text-sm text-neutral-800 ${
                        route.name === "Closet" ? "font-bold" : ""
                    }`}
                >
                    Closet
                </Text>
            </Pressable>
            <Pressable
                className="flex flex-col items-center p-3"
                onPress={() => navigation.navigate("Account")}
            >
                <Ionicons
                    name={
                        route.name === "Account" ? "person" : "person-outline"
                    }
                    size={24}
                    color="#262626"
                />
                <Text
                    className={`text-sm text-neutral-800 ${
                        route.name === "Account" ? "font-bold" : ""
                    }`}
                >
                    Account
                </Text>
            </Pressable>
        </View>
    );
}
