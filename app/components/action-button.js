import { useNavigation, useRoute } from "@react-navigation/native";
import { Pressable, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";

export default function ActionButton({ value, setModalVisible }) {
    const navigation = useNavigation();

    return (
        <Pressable
            className="absolute bottom-24 right-5 p-4 bg-neutral-800 rounded-full flex flex-row justify-center items-center"
            onPress={() => {
                setModalVisible(true);
            }}
        >
            <Ionicons name="add-outline" size={24} color="#fff" />
            <Text className="text-white ml-2 font-semibold">{value}</Text>
        </Pressable>
    );
}
