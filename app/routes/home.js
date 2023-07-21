import {
    KeyboardAvoidingView,
    Modal,
    Pressable,
    Text,
    TextInput,
    View,
} from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { useAuth } from "../AuthContext";
import Navigation from "../components/navigation";
import ActionButton from "../components/action-button";
import Header from "../components/header";
import { useState } from "react";
import Ionicons from "@expo/vector-icons/Ionicons";
import * as ImagePicker from "expo-image-picker";

export default function Home({ navigation }) {
    const { onLogout } = useAuth();
    const [modalVisible, setModalVisible] = useState(false);
    const [dropdown, setDropdown] = useState(false);
    const [type, setType] = useState("");
    const types = [
        { label: "T-shirts", value: "t-shirts" },
        { label: "Shirts", value: "shirts" },
        { label: "Pants", value: "pants" },
        { label: "Coats", value: "coats" },
        { label: "Hats", value: "hats" },
        { label: "Jackets", value: "jackets" },
        { label: "Caps", value: "caps" },
        { label: "Skirts", value: "skirts" },
        { label: "Socks", value: "socks" },
        { label: "Shoes", value: "shoes" },
    ];

    async function logOut() {
        await onLogout();
    }

    function uploadImage() {

    }

    return (
        <View className="h-screen">
            <Header />
            <View className="flex flex-row justify-center items-center h-screen">
                <Text className="text-lg font-semibold">No outfits yet!</Text>
            </View>
            <ActionButton
                value="Add Outfit"
                setModalVisible={setModalVisible}
            />
            <Navigation />
            <Modal
                visible={modalVisible}
                animationType="fade"
                transparent={true}
            >
                <KeyboardAvoidingView
                    className="w-full h-screen flex flex-col justify-end bg-black/10"
                    behavior="height"
                >
                    <View className="p-4 bg-white">
                        <View className="flex flex-row justify-between">
                            <Text className="text-lg font-semibold mb-4">
                                New Outfit
                            </Text>
                            <Pressable onPress={() => setModalVisible(false)}>
                                <Ionicons name="close" size={24} />
                            </Pressable>
                        </View>
                        <TextInput
                            placeholder="Name"
                            className="py-1 px-3 border rounded-sm border-neutral-200 text-sm w-full focus:border-neutral-800 mb-4"
                        />
                        <TextInput
                            placeholder="Brand"
                            className="py-1 px-3 border rounded-sm border-neutral-200 text-sm w-full focus:border-neutral-800 mb-4"
                        />
                        <Pressable
                            className="py-2 px-3 border rounded-sm border-neutral-200 w-full mb-4"
                            onPress={uploadImage}
                        >
                            <Text className="text-sm">Add Image</Text>
                        </Pressable>
                        <DropDownPicker
                            open={dropdown}
                            value={type}
                            items={types}
                            setOpen={setDropdown}
                            setValue={setType}
                            className="mb-4"
                        />
                        <Pressable
                            className="py-3 px-3 border rounded-sm border-neutral-200 w-full mb-4 bg-neutral-800 flex justify-center items-center"
                            onPress={() => setModalVisible(false)}
                        >
                            <Text className="text-sm text-white font-bold">
                                Save Outfit
                            </Text>
                        </Pressable>
                    </View>
                </KeyboardAvoidingView>
            </Modal>
        </View>
    );
}
