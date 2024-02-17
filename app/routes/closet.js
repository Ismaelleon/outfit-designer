import {
    Alert,
    Image,
    KeyboardAvoidingView,
    Modal,
    Pressable,
    Text,
    TextInput,
    View,
} from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { API_URL, useAuth } from "../AuthContext";
import Navigation from "../components/navigation";
import ActionButton from "../components/action-button";
import Header from "../components/header";
import { useState } from "react";
import Ionicons from "@expo/vector-icons/Ionicons";
import * as ImagePicker from "expo-image-picker";
import * as Permissions from "expo-permissions";
import axios from "axios";

export default function Closet() {
    const { onLogout } = useAuth();
    const [name, setName] = useState("");
    const [brand, setBrand] = useState("");
    const [image, setImage] = useState(null);
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

    async function openGallery() {
        try {
            let result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
                allowsEditing: true,
                aspect: [1, 1],
                quality: 1,
            });

            if (!result.canceled) {
                setImage(result.assets[0]);
            }
        } catch (error) {
            console.log(error);
        }
    }

    async function openCamera() {
        try {
            let result = await ImagePicker.launchCameraAsync({
                allowsEditing: true,
                aspect: [1, 1],
                quality: 1
            })

            if (!result.canceled) {
                setImage(result.assets[0]);
            }
        } catch (error) {
            console.log(error);
        }
    }

    async function logOut() {
        await onLogout();
    }

    async function saveClothes() {
        try {
            const result = await axios.postForm(`${API_URL}/new-clothes`, {
                name,
                brand,
                type,
                image: image.base64,
            });

            setModalVisible(false);
        } catch (error) {
            console.log(error);
        }
    }

    return (
        <View className="h-screen">
            <Header />
            <View className="flex flex-row justify-center items-center h-screen">
                <Text className="text-lg font-semibold">No clothes yet!</Text>
            </View>
            <ActionButton
                value="Add Clothes"
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
                                New Clothes
                            </Text>
                            <Pressable onPress={() => setModalVisible(false)}>
                                <Ionicons name="close" size={24} />
                            </Pressable>
                        </View>
                        <TextInput
                            placeholder="Name"
                            className="py-1 px-3 border rounded-sm border-neutral-200 text-sm w-full focus:border-neutral-800 mb-4"
                            onChangeText={setName}
                            value={name}
                        />
                        <TextInput
                            placeholder="Brand"
                            className="py-1 px-3 border rounded-sm border-neutral-200 text-sm w-full focus:border-neutral-800 mb-4"
                            onChangeText={setBrand}
                            value={brand}
                        />
                        {image ? (
                            <View className="flex flex-col items-center">
                                <Image className="self-center mb-2" source={{ uri: image.uri }} style={{ width: 200, height: 200 }} />
                                <Pressable className="p-2 border rounded-sm border-neutral-200 mb-4" onPress={() => setImage(null)}>
                                    <Ionicons name="close-outline" color="rgb(239, 68, 68)" size={24}  />
                                </Pressable>
                            </View>
                        ) : (
                            <View className="flex flex-row justify-between w-full">
                                <Pressable
                                    className="flex items-center flex-col py-2 px-3 border rounded-sm border-neutral-200 mb-4 w-[48%]"
                                    onPress={openCamera}
                                >
                                    <Ionicons name="camera" size={24} />
                                    <Text className="text-sm text-gray-600">Take Photo</Text>
                                </Pressable>
                                <Pressable
                                    className="flex items-center flex-col py-2 px-3 border rounded-sm border-neutral-200 mb-4 w-[48%]"
                                    onPress={openGallery}
                                >
                                    <Ionicons name="images" size={24} />
                                    <Text className="text-sm text-gray-600">Select image</Text>
                                </Pressable>
                            </View>
                        )}
                        <DropDownPicker
                            open={dropdown}
                            value={type}
                            items={types}
                            setOpen={setDropdown}
                            setValue={setType}
                            className="mb-4"
                            dropDownDirection="TOP"
                            style={{
                                borderColor: "#262626",
                                color: "#262626",
                            }}
                            placeholder="Type"
                        />
                        <Pressable
                            className="py-3 px-3 border rounded-sm border-neutral-200 w-full mb-4 bg-neutral-800 flex justify-center items-center"
                            onPress={saveClothes}
                        >
                            <Text className="text-sm text-white font-bold">
                                Save Clothes
                            </Text>
                        </Pressable>
                    </View>
                </KeyboardAvoidingView>
            </Modal>
        </View>
    );
}
