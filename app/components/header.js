import { Text, View } from "react-native";

export default function Header() {
    return (
        <View className="mt-4 py-3 px-4 border-b border-neutral-200 fixed -top-4 left-0 bg-white">
            <Text className="text-xl font-bold">Outfit Designer </Text>
        </View>
    );
}
